#!/usr/bin/python
# DigitalOcean droplet information parser:
# - Fetch Droplet ID by known Public IPv4
#   Pass IPv4 as input parameters
#   Usage example: python droplet_parser.py -ip X.X.X.X
# - Fetch Private IP list in json format by known Droplet name
#   Pass Droplet name or mask as input parameters
#   Usage example: python droplet_parser.py -f webserver-
# - Fetch DigitalOcean inventory dictionary for account
#   Usage example: python droplet_parser.py -list
# - Fetch DigitalOcean simple public iplist for account
#   Usage example: python droplet_parser.py -iplist
# - Fetch DigitalOcean inventory dictionary of droplets with volumes for account
#   Usage example: python droplet_parser.py -volumes
# - Fetch DigitalOcean inventory dictionary of droplets images for account
#   Usage example: python droplet_parser.py -images
#
# - Handle as many DigitalOcean pages as needed, for large projects.
#   Usage example: python droplet_parser.py -list -pages <number>
#
#   DO API key should be set in following format:
#   export DO_API_TOKEN=<secret_key>
#
# Author: Svyatoslav Lazarev (silazare.nsk@gmail.com)
	
	
import os
import sys
import re
import json
import requests
import argparse
from sys import argv
from pprint import pprint

# API key environment check
try:
    api_key = os.environ['DO_API_TOKEN']
except KeyError:
    print('Set DO_API_TOKEN before use:')
    print('export DO_API_TOKEN=<token>')
    sys.exit(1)

# Functions	
def get_nest_data(url,token):
    '''
    function for API call to DigitalOcean
    return raw dictionary in json format
    '''
    auth_t = token.encode("ascii", "ignore")
    headers = {
        'authorization': "Bearer " + auth_t,
        'content-type': "application/json",
    }

    try:
        init_res = requests.get(url, headers=headers, allow_redirects=False)
        if init_res.status_code == 307:
            api_response = requests.get(init_res, headers=headers, allow_redirects=False)
            if api_response.status_code == 200:
                return api_response.json()
        elif init_res.status_code == 200:
            return init_res.json()
        elif init_res.status_code == 401:
            print('Unauthorized API request, check your DO_API_TOKEN')
            sys.exit(0)
    except Exception as ce:
        print(ce)

def get_inventory(templates):
    '''
    function to get all droplets inventory from DigitalOcean
    '''
    hostname = {}   
    for i in templates:
        # j is a json dict of each droplet data
        for j in templates[i]:
            try:
                inventory = []
                for k in j:
                    if k in ('name'):
                        key = j[k].encode('ascii')
                    elif k in ('id', 'size_slug'):
                        try:
                            inventory.append(j[k].encode('ascii'))
                        except AttributeError:
                            inventory.append(j[k])                         
                    elif k in 'networks':
                        inventory.append(j[k]['v4'][0]['ip_address'].encode('ascii'))
                if key not in hostname:
                    hostname[key] = inventory
                else:
                    hostname[key].append(inventory)
            except TypeError:
                continue
    return(hostname)

def get_id(templates,ipaddr):
    '''
    function to get droplet id by known Public IP
    '''
    for i in templates:
        for j in templates[i]:
           for k in j:
               if k == 'id':
                   if j['networks']['v4'][0]['ip_address'] == ipaddr:
                      return j[k]

def get_private_ip(templates,criteria):
    '''
    function to get Private IP list for known droplet name regex
    '''
    dict = {}
    regex = ('^' + criteria)
    for i in templates:
            for j in templates[i]:
                for k in j:
                    if k == 'name':
                        if re.match(regex, j[k]):
                            if re.match('^10.\d{1,3}.\d{1,3}.\d{1,3}$', j['networks']['v4'][1]['ip_address']):
                                dict[j[k].encode('ascii')] = [j['networks']['v4'][1]['ip_address'].encode('ascii')]
                            else:
                                dict[j[k].encode('ascii')] = [j['networks']['v4'][0]['ip_address'].encode('ascii')]
    return(dict)

def get_map_volumes(templates):
    '''
    function to get droplets and volumes mapped with it from DigitalOcean
    '''
    hostname = {}   
    for i in templates:
        # j is a json dict of each droplet data
        for j in templates[i]:
            try:
                inventory = []
                for k in j:
                    if k in ('name'):
                        key = j[k].encode('ascii')
                    elif k in ('id'):
                        inventory.append(j[k])
                    elif k in ('volume_ids'):
                        if len(j[k]) > 0:
                            # encode volumes list and append it as an item to dict values list
                            inventory.append([x.encode('ascii') for x in j[k]])                 
                if key not in hostname:
                    hostname[key] = inventory
                else:
                    hostname[key].append(inventory)
            except TypeError:
                continue
    hostname_vol = {k : v for k,v in hostname.iteritems() if len(v) > 1 and type(v[0]) == list}
    return(hostname_vol)

def get_images(templates):
    '''
    function to get all images inventory from DigitalOcean
    '''
    image = {}   
    for i in templates:
        # j is a json dict of each droplet data
        for j in templates[i]:
            try:
                inventory = []
                for k in j:
                    if k in ('name'):
                        key = j[k].encode('ascii')
                    elif k in ('id', 'distribution','type'):
                        try:
                            inventory.append(j[k].encode('ascii'))
                        except AttributeError:
                            inventory.append(j[k])                         
                if key not in image:
                    image[key] = inventory
                else:
                    image[key].append(inventory)
            except TypeError:
                continue
    return(image)
	
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Digital Ocean droplets parse script')
    parser.add_argument('-ip', action="store", dest="ip")
    parser.add_argument('-f', action="store", dest="filter")
    parser.add_argument('-list', action='store_true', dest="list")
    parser.add_argument('-iplist', action='store_true', dest="iplist")
    parser.add_argument('-images', action='store_true', dest="images")    
    parser.add_argument('-volumes', action='store_true', dest="volumes")
    parser.add_argument('-pages', action="store", dest="pages", type=int, nargs='?', const=1, default=1)
    args = parser.parse_args()

    link = []
    for item in range(1,args.pages+1): 
        link.append("https://api.digitalocean.com/v2/droplets?page=" + str(item) + "&per_page=999")

    link_img = []
    for item in range(1,args.pages+1): 
        link_img.append("https://api.digitalocean.com/v2/images?private=true&page=" + str(item) + "&per_page=999")

    if args.ip is not None:
        result = None
        try:
            list_id = []
            for k in link:
                list_id.append(get_id(get_nest_data(k,api_key),args.ip))
            filtered_list_id = filter(None, list(set(list_id)))
            result = filtered_list_id[0]
        except IndexError:
            pass
        except TypeError:
            pass
        if result is None:
            print("No such droplet IP address found in your account.")
        else:
            print(result)
    elif args.filter is not None:
        droplets = {}
        for k in link:
            droplets.update(get_private_ip(get_nest_data(k,api_key),args.filter))
        if droplets:
            for k, v in droplets.iteritems():
                print ('{0:<45}  {1:^10}'.format(k, v))
        else:
            print("No such droplet name found in your account.")
    elif args.list:
        hosts = {}
        for k in link:
            hosts.update(get_inventory(get_nest_data(k,api_key)))
        if hosts:
            for k, v in hosts.iteritems():
                print ('{0:<45}  {1:^10}'.format(k, v))
        else:
            print("No droplets found in your account.")            
    elif args.iplist:
        hosts = {}
        for k in link:
            hosts.update(get_inventory(get_nest_data(k,api_key)))
        if hosts:
            for k, v in hosts.iteritems():
                print ('{0:<45}  {1:^10}'.format(k, v[1]))
        else:
            print("No droplets found in your account.") 
    elif args.volumes:
        map_volumes = {}
        for k in link:
            map_volumes.update(get_map_volumes(get_nest_data(k,api_key)))
        if map_volumes:
            for k, v in map_volumes.iteritems():
                print ('{0:<45}  {1:^10}'.format(k, v))
        else:
            print("No droplets with volumes found in your account.")
    elif args.images:
        images = {}
        for k in link_img:
            images.update(get_images(get_nest_data(k,api_key)))
        if images:
            for k, v in images.iteritems():
                print ('{0:<45}  {1:^10}'.format(k, v))
        else:
            print("No custom droplet images found in your account.")
    else:
        print('Please pass correct input parameter')