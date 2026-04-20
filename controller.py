from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, arp


class HostDiscovery(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(HostDiscovery, self).__init__(*args, **kwargs)

        self.mac_to_port = {}
        self.host_db = {}
        self.installed_flows = set()
        self.packet_count = 0

        print("\n========== HOST DISCOVERY SERVICE STARTED ==========")

    # ---------------------------------------------
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):

        datapath = ev.msg.datapath
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        print("[SWITCH CONNECTED] s1 connected")

        match = parser.OFPMatch()

        actions = [
            parser.OFPActionOutput(
                ofproto.OFPP_CONTROLLER,
                ofproto.OFPCML_NO_BUFFER
            )
        ]

        self.add_flow(datapath, 0, match, actions)

    # ---------------------------------------------
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):

        msg = ev.msg
        datapath = msg.datapath
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        if not eth:
            return

        src = eth.src
        dst = eth.dst
        in_port = msg.match['in_port']

        if dst.startswith("33:33"):
            return

        if eth.ethertype == 35020:
            return

        self.packet_count += 1
        print(f"[PACKET COUNT] {self.packet_count}")

        ip_addr = "Unknown"
        arp_pkt = pkt.get_protocol(arp.arp)
        if arp_pkt:
            ip_addr = arp_pkt.src_ip

        # -----------------------------------------
        # HOST DISCOVERY
        # -----------------------------------------
        changed = False

        if src not in self.host_db:
            self.host_db[src] = {
                "ip": ip_addr,
                "switch": dpid,
                "port": in_port
            }
            print(f"[HOST DISCOVERED] {src}")
            changed = True

        else:
            if self.host_db[src]["port"] != in_port:
                print(f"[HOST MOVED] {src}")
                self.host_db[src]["port"] = in_port
                changed = True

        self.mac_to_port[dpid][src] = in_port

        if changed:
            self.show_hosts()

        # -----------------------------------------
        # BLOCK h3 -> h1
        # -----------------------------------------
        if src == "00:00:00:00:00:03" and dst == "00:00:00:00:00:01":
            print("[BLOCKED] h3 denied access to h1")
            return

        # -----------------------------------------
        # FORWARD
        # -----------------------------------------
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # -----------------------------------------
        # INSTALL FLOW ONCE
        # -----------------------------------------
        if out_port != ofproto.OFPP_FLOOD:

            flow_key = (src, dst, in_port)

            if flow_key not in self.installed_flows:

                match = parser.OFPMatch(
                    in_port=in_port,
                    eth_src=src,
                    eth_dst=dst
                )

                priority = 10 if (
                    (src == "00:00:00:00:00:01" and dst == "00:00:00:00:00:02")
                    or
                    (src == "00:00:00:00:00:02" and dst == "00:00:00:00:00:01")
                ) else 1

                if priority == 10:
                    print("[QOS] High priority flow h1 <-> h2")

                self.add_flow(datapath, priority, match, actions)

                print(f"[FLOW INSTALLED] {src} -> {dst}")

                self.installed_flows.add(flow_key)

        out = parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=msg.data
        )

        datapath.send_msg(out)

    # ---------------------------------------------
    def show_hosts(self):

        print("\n========== HOST DATABASE ==========")

        for mac, data in self.host_db.items():
            print(
                f"MAC:{mac} | IP:{data['ip']} | "
                f"Switch:{data['switch']} | Port:{data['port']}"
            )

        print("===================================")

    # ---------------------------------------------
    def add_flow(self, datapath, priority, match, actions):

        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        inst = [
            parser.OFPInstructionActions(
                ofproto.OFPIT_APPLY_ACTIONS,
                actions
            )
        ]

        mod = parser.OFPFlowMod(
            datapath=datapath,
            priority=priority,
            match=match,
            instructions=inst,
            idle_timeout=30
        )

        datapath.send_msg(mod)