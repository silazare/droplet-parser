## Droplet parser

![language](https://img.shields.io/badge/language-python-blue.svg)

### Description:
DigitalOcean Droplets info parsing tool:

- Fetch ID for further DO API actions (reboot,power_cycle etc.)
- Generate Private IP list in json dictionary according Droplet name
- Generate DigitalOcean droplets inventory in dictionary
- Generate DigitalOcean droplets Public IP list
- Generate DigitalOcean droplets volumes and images details
- Handle as many DigitalOcean pages as needed, for large projects

### Usage:

- Clone this repository to your folder:
```sh
$ git clone https://github.com/silazare/droplet-parser.git
$ cd droplet_parser
```

- Add your secret DO API key in env before use:
```sh
export DO_API_TOKEN=<secret_key>
```

- Execute to find ID by known IPv4:
```sh
$ python droplet_parser.py -ip <IPv4>
Where: 
      <IPv4> - IPv4 address in general octet format
```

- Execute to generate Private IPv4 list by known name/mask:
```sh
$ python droplet_parser.py -f <NAME MASK>
Where:
      <NAME MASK> - Droplet name in general string format (ex. webserver-)
```

- Execute to generate droplets inventory list:
```sh
$ python droplet_parser.py -list
Output format:
      { <droplet_name>: [<size>, <public ip>, <droplet id> ] }
```

- Execute to generate droplets Public IPv4 list:
```sh
$ python droplet_parser.py -iplist
Output format:
      { <droplet_name>: <public ip> }
```

- Execute to generate inventory list of droplets with volumes:
```sh
$ python droplet_parser.py -volumes
Output format:
      { <droplet_name>: [[<list_of_volume_ids>], <droplet id> ] }
```

- Execute to generate inventory list of droplets custom images:
```sh
$ python droplet_parser.py -images
Output format:
      { <droplet_name>: [<image id>, <os type>, <image type> ] }
```

## Additional options

For large infrastructures you may use *-pages* argument with any other arguments, it works like you turn the pages in yout Digital Ocean web console. By default there is 1 page with 999 items on it, as far as I know it is maximum default.
Example of usage:
```sh
$ python droplet_parser.py -list -pages 4
```