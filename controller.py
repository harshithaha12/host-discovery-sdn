from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet


class SimpleSDN(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSDN, self).__init__(*args, **kwargs)

        # MAC learning table
        self.mac_to_port = {}

        # Host discovery table
        self.host_table = {}

        # Statistics
        self.packet_count = 0

    # -------------------------------------------------
    # Switch Connection + Default Table Miss Rule
    # -------------------------------------------------
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        print("\n[SWITCH CONNECTED] s1 connected to controller")

        # Send unknown packets to controller
        match = parser.OFPMatch()

        actions = [
            parser.OFPActionOutput(
                ofproto.OFPP_CONTROLLER,
                ofproto.OFPCML_NO_BUFFER
            )
        ]

        self.add_flow(datapath, 0, match, actions)

    # -------------------------------------------------
    # Main Packet Handler
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

        if not eth:
            return

        src = eth.src
        dst = eth.dst
        in_port = msg.match['in_port']

        # Ignore multicast noise
        if dst.startswith("33:33"):
            return

        # Ignore LLDP
        if eth.ethertype == 35020:
            return

        # ---------------------------------------------
        # Statistics
        # ---------------------------------------------
        self.packet_count += 1
        print(f"[PACKET COUNT] {self.packet_count}")

        # ---------------------------------------------
        # Host Discovery
        # ---------------------------------------------
        if src not in self.host_table:
            self.host_table[src] = {
                "switch": dpid,
                "port": in_port
            }

            print(f"[HOST DISCOVERED] {src} at port {in_port}")

        # Learn source MAC
        self.mac_to_port[dpid][src] = in_port

        # ---------------------------------------------
        # Firewall / Blocking Policy
        # Block h3 -> h1
        # ---------------------------------------------
        if src == "00:00:00:00:00:03" and dst == "00:00:00:00:00:01":
            print("[BLOCKED] h3 denied access to h1")
            return

        # ---------------------------------------------
        # Forwarding Logic
        # ---------------------------------------------
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # ---------------------------------------------
        # Flow Rule Installation
        # QoS Upgrade:
        # h1 <-> h2 gets higher priority = 10
        # Others priority = 1
        # ---------------------------------------------
        if out_port != ofproto.OFPP_FLOOD:

            match = parser.OFPMatch(
                in_port=in_port,
                eth_src=src,
                eth_dst=dst
            )

            # High priority traffic for h1 <-> h2
            if (
                (src == "00:00:00:00:00:01" and dst == "00:00:00:00:00:02")
                or
                (src == "00:00:00:00:00:02" and dst == "00:00:00:00:00:01")
            ):
                priority = 10
                print("[QOS] High priority flow for h1 <-> h2")

            else:
                priority = 1

            self.add_flow(datapath, priority, match, actions)

            print(f"[FLOW INSTALLED] {src} -> {dst}")

        # ---------------------------------------------
        # Send Packet Out
        # ---------------------------------------------
        out = parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=msg.data
        )

        datapath.send_msg(out)

    # -------------------------------------------------
    # Flow Rule Helper
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
            instructions=inst
        )

        datapath.send_msg(mod)