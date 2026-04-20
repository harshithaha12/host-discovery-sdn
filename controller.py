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
        self.packet_count = 0

        print("\n========== HOST DISCOVERY SERVICE STARTED ==========")

    # -------------------------------------------------
    # Switch Connected
    # -------------------------------------------------
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):

        datapath = ev.msg.datapath
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        print("[SWITCH CONNECTED] s1 connected")

        # Table Miss Rule
        match = parser.OFPMatch()

        actions = [
            parser.OFPActionOutput(
                ofproto.OFPP_CONTROLLER,
                ofproto.OFPCML_NO_BUFFER
            )
        ]

        self.add_flow(datapath, 0, match, actions)

    # -------------------------------------------------
    # Packet In Handler
    # -------------------------------------------------
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

        if eth is None:
            return

        src = eth.src
        dst = eth.dst
        in_port = msg.match['in_port']

        # Ignore LLDP
        if eth.ethertype == 35020:
            return

        # Ignore IPv6 multicast noise
        if dst.startswith("33:33"):
            return

        # -----------------------------------------
        # Packet Count
        # -----------------------------------------
        self.packet_count += 1
        print(f"[PACKET COUNT] {self.packet_count}")

        # -----------------------------------------
        # Learn Source MAC
        # -----------------------------------------
        self.mac_to_port[dpid][src] = in_port

        # -----------------------------------------
        # Host Discovery Database
        # -----------------------------------------
        ip_addr = "Unknown"

        arp_pkt = pkt.get_protocol(arp.arp)
        if arp_pkt:
            ip_addr = arp_pkt.src_ip

        if src not in self.host_db:
            self.host_db[src] = {
                "ip": ip_addr,
                "switch": dpid,
                "port": in_port
            }

            print(f"[HOST DISCOVERED] {src}")
            self.show_hosts()

        else:
            self.host_db[src]["port"] = in_port
            self.host_db[src]["switch"] = dpid

            if ip_addr != "Unknown":
                self.host_db[src]["ip"] = ip_addr

        # -----------------------------------------
        # Firewall Rule
        # Block ONLY h3 -> h1
        # -----------------------------------------
        if (
            src == "00:00:00:00:00:03"
            and dst == "00:00:00:00:00:01"
        ):
            print("[BLOCKED] h3 denied access to h1")
            return

        # -----------------------------------------
        # Forwarding Logic (WORKING)
        # -----------------------------------------
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # -----------------------------------------
        # Install Flow ONLY when destination known
        # -----------------------------------------
        if out_port != ofproto.OFPP_FLOOD:

            match = parser.OFPMatch(
                in_port=in_port,
                eth_src=src,
                eth_dst=dst
            )

            # QoS Priority
            if (
                (src == "00:00:00:00:00:01" and dst == "00:00:00:00:00:02")
                or
                (src == "00:00:00:00:00:02" and dst == "00:00:00:00:00:01")
            ):
                priority = 10
                print("[QOS] High priority flow h1 <-> h2")
            else:
                priority = 1

            self.add_flow(datapath, priority, match, actions)
            print(f"[FLOW INSTALLED] {src} -> {dst}")

        # -----------------------------------------
        # IMPORTANT FIX:
        # Send data=None if switch buffered packet
        # -----------------------------------------
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=data
        )

        datapath.send_msg(out)

    # -------------------------------------------------
    # Show Host DB
    # -------------------------------------------------
    def show_hosts(self):

        print("\n========== HOST DATABASE ==========")

        for mac, info in self.host_db.items():
            print(
                f"MAC: {mac} | "
                f"IP: {info['ip']} | "
                f"Switch: {info['switch']} | "
                f"Port: {info['port']}"
            )

        print("===================================\n")

    # -------------------------------------------------
    # Add Flow Helper
    # -------------------------------------------------
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