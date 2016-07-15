import os
import sys
import argparse
import requests
import json

from beluga.api.auth import BelugaAPIAuth


def error(message):
    print message
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='BelugaCDN API Tool')
    parser.add_argument('--token-id', dest='token_id', default=os.environ.get("BELUGA_TOKEN_ID", None),
                        help='API Token ID, may be specified with BELUGA_TOKEN_SECRET environment variable')
    parser.add_argument('--token-secret', dest='token_secret', default=os.environ.get("BELUGA_TOKEN_SECRET", None),
                        help='API Token Secret, may be specified with BELUGA_TOKEN_SECRET environment variable')
    parser.add_argument('--username', dest='username', default=os.environ.get("BELUGA_USERNAME", None),
                        help='Beluga account username, may be specified with BELUGA_USERNAME environment variable')
    parser.add_argument('--password', dest='password', default=os.environ.get("BELUGA_PASSWORD", None),
                        help='Beluga account password, may be specified with BELUGA_PASSWORD environment variable')
    parser.add_argument('--base-url', dest='base_url', default=os.environ.get("BELUGA_BASE_URL", 'https://api.belugacdn.com'),
                        help='API Base URL')
    parser.add_argument(
        '--body', dest='body', help='JSON body to post, prepend with @ to read from file', default=None)
    parser.add_argument(
        '--method', dest='method', default='GET', help='GET|POST|PUT|DELETE')
    parser.add_argument(
        '--service', dest='service', default='api/cdn/v2', help='API Service Name')
    parser.add_argument(
        '--path', dest='path', default='identity', help='API Request Path')
    parser.add_argument('--pretty', dest='pretty', default=False,
                        help='prettify JSON output', action='store_true')
    parser.add_argument('--print', dest='print', default=False,
                        help='print JSON result to stdout', action='store_true')
    parser.add_argument('--silent', dest='silent', default=False,
                        help='inhibit default json result printing', action='store_true')
    parser.add_argument('--accept', dest='accept',
                        default='application/json', help='accept content-type')
    parser.add_argument(
        '--write', dest='write', default=False, help='write JSON result to a file')

    args = parser.parse_args()
    headers = {}
    ssl_verify = True

    if args.token_id is not None and args.token_secret is not None:
        auth = BelugaAPIAuth(id=args.token_id, secret=args.token_secret)
    elif args.username is not None and args.password is not None:
        auth = BelugaAPIAuth(username=args.username, password=args.password)

    else:
        error(
            "--token-id and --token-secret or --username and --password are required")

    if args.silent is False and getattr(args, 'print') is False and args.write is False:
        setattr(args, 'print', True)
        args.pretty = True

    headers['Accept'] = args.accept

    if args.body:
        if args.method not in ['POST', 'PUT']:
            error("method must be POST|PUT if body is specified")
        headers['Content-type'] = 'application/json'
        if args.body[0] == "@":
            body_fh = open(args.body[1:], "r")
            body_json = json.load(body_fh)
            body_fh.close()
        else:
            body_json = json.loads(args.body)
        body = json.dumps(body_json)
    else:
        if args.method not in ['GET', 'DELETE']:
            error("method must be GET|DELETE if body is not specified")
        body = None

    if len(args.service) > 0:
        url = "%s/%s/%s" % (args.base_url, args.service, args.path)
    else:
        url = "%s/%s" % (args.base_url, args.path)

    response = requests.request(
        args.method, url, auth=auth, headers=headers, data=body, verify=ssl_verify)

    if args.accept == 'application/json':
        try:
            json_response = json.loads(response.text)
        except ValueError:
            print response.text
            return
        if getattr(args, 'print'):
            if args.pretty:
                print json.dumps(json_response, indent=4)
            else:
                print json.dumps(json_response)
        if args.write:
            write_fh = open(args.write, "w")
            if args.pretty:
                json.dump(write_fh, json_response, indent=4)
            else:
                json.dump(write_fh, json_response)
            write_fh.close()
    else:
        print response.text

if __name__ == "__main__":
    main()
