#!/usr/bin/env python3
import argparse
import socket

from tcppinglib import tcpping

parser = argparse.ArgumentParser(description='PING over TCP')
parser.add_argument('host', type=str, help='host')
parser.add_argument('port', type=int, help='port')
parser.add_argument('-i', metavar='WAIT', type=float, default=1, help='wait (seconds) between pings')
parser.add_argument('-n', metavar='COUNT', type=int, default=5, help='count of pings, use 0 for infinite')
parser.add_argument('-t', metavar='TIMEOUT', type=float, default=5, help='timeout (seconds) of a single pin')

parser.add_argument('--rtt', type=float, default=None, nargs=2, help='checkmk warn/crit level for RTT (ms)')
parser.add_argument('--loss', type=float, default=None, nargs=2, help='checkmk warn/crit level for loss (%%)')
parser.add_argument('--name', type=str, default=None, help='checkmk additional text in service name')

if __name__ == "__main__":
    try:
        args = parser.parse_args()

        if args.rtt is None and args.loss is None:
            print(f"TCPING {args.host}:{args.port} ({socket.gethostbyname(args.host)}): handshake")

        ret = tcpping(args.host, args.port, timeout=args.t, count=args.n, interval=args.i)

        if args.rtt is None and args.loss is None:
            print(f"""--- {args.host}:{args.port} tcping statistics ---
{ret.packets_sent} handshakes initiated, {ret.packets_received} handshakes completed, {ret.packet_loss}% handshakes failed
round-trip min/avg/max/stddev = {ret.min_rtt:.3f}/{ret.avg_rtt:.3f}/{ret.max_rtt:.3f}/xx.xxx ms
""")
        else:
            kpis = []
            if args.rtt is not None:
                kpis.append(f"rtt={ret.avg_rtt};{args.rtt[0]};{args.rtt[1]}")
            if args.loss is not None:
                kpis.append(f"loss={ret.packet_loss};{args.loss[0]};{args.loss[1]}")

            if ret.is_alive:
                print(
                    f'P "tcping{" " + args.name if args.name is not None else ""} {args.host}:{args.port}" {"|".join(kpis)} {ret.packets_sent} handshakes initiated')
            else:
                print(
                    f'2 "tcping{" " + args.name if args.name is not None else ""} {args.host}:{args.port}" {"|".join(kpis)} host down')

    except KeyboardInterrupt:
        exit(0)
    except Exception as e:
        if 'rtt' in args and 'loss' in args is None:
            print(e)
        else:
            print(f'3 "tcping{" " + args.name if args.name is not None else ""} {args.host}:{args.port}" - Error: {e}')
        exit(1)
