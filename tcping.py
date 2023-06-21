#!/usr/bin/env python3
import argparse
import socket

from tcppinglib import tcpping

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('host', type=str, help='host')
parser.add_argument('port', type=int, help='port')
parser.add_argument('-i', type=float, default=1, help='wait')
parser.add_argument('-n', type=int, default=5, help='count, use 0 for infinite')
parser.add_argument('-t', type=float, default=5, help='timeout')

parser.add_argument('--rtt', type=float, nargs=2, default=None, help='warn/crit level for RTT (ms)')
parser.add_argument('--loss', type=float, nargs=2, default=None, help='warn/crit level for loss (%)')

if __name__ == "__main__":
    try:
        args = parser.parse_args()

        if args.rtt is None and args.loss is None:
            print(f"TCPING {args.host}:{args.port} ({socket.gethostbyname(args.host)}): handshake")

        ret = tcpping(args.host, args.port, timeout=args.t, count=args.n, interval=args.i)

        if args.rtt is None and args.loss is None:
            print(f"""--- {args.host}:{args.port} tcping statistics ---
{ret.packets_sent} packets transmitted, {ret.packets_received} packets received, {ret.packet_loss}% packet loss
round-trip min/avg/max/stddev = {ret.min_rtt:.3f}/{ret.avg_rtt:.3f}/{ret.max_rtt:.3f}/xx.xxx ms
""")
        else:
            kpis = []
            if args.rtt is not None:
                kpis.append(f"rtt={ret.avg_rtt};{args.rtt[0]};{args.rtt[1]}")
            if args.loss is not None:
                kpis.append(f"loss={ret.packet_loss};{args.loss[0]};{args.loss[1]}")

            if ret.is_alive:
                print(f'P "tcping {args.host}:{args.port}" {"|".join(kpis)} {ret.packets_sent} packet sent')
            else:
                print(f'2 "tcping {args.host}:{args.port}" {"|".join(kpis)} host down')

    except KeyboardInterrupt:
        exit(0)
    except Exception as e:
        if args.rtt is None and args.loss is None:
            print(e)
        else:
            print(f'3 "tcping {args.host}:{args.port}" - Error: {e}')
        exit(1)
