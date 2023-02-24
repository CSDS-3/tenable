from tenable.io import TenableIO
from pysnipeit import SnipeIT
import logging

snipe = SnipeIT()
tio = TenableIO()
logging.basicConfig(level='INFO', format='%(asctime)s - %(levelname)s - %(message)s')

def force_list_to_str(val):
    '''For some reason tenable will use lists for values that 
    can only ever be a str'''    
    return val[0] if isinstance(val,list) else val
    
def tio_assets():
    logging.info('Pulling all assets with details')
    try:
        return [tio.assets.details(i['id']) for i in tio.assets.list()]
    except:
        logging.exception('TIO API fail')

def process_assets(assets):
    logging.info(f'Processing {len(assets)} against snipe_it')
    if not assets:
        logging.info('No assets returned')
        return
    for asset in assets:
        formatted_asset = format_asset(asset=asset)
        send_to_snipeIT(asset=formatted_asset)

def send_to_snipeIT(asset):
    result = snipe.assets.update(asset)
    logging.debug(f'SnipeIT asset update {result=}')

def lookup_snipe_it_name(function, name):
    return next((i['id'] for i in getattr(snipe,function).list() if i['name']==name), None)

def format_asset(asset):
    try:
        ec2_id = force_list_to_str(asset.get('aws_ec2_instance_id'))    
        name = force_list_to_str(asset.get('hostname'))
        data = {
            'asset_tag': ec2_id,
            'status_id': snipeIT_lookup['status_id'],
            'model_id': snipeIT_lookup['model_id'],
            'name' : name
            }
    except:
        logging.exception(f'Formatting error {asset=}')
    logging.debug(f'Formatted {asset=} to {data=}')
    return data

def build_snipeIT_lookup():
    global snipeIT_lookup
    try:
        status_id = lookup_snipe_it_name(function='status_labels', name='Ready to Deploy')
        model_id = lookup_snipe_it_name(function='models', name='AWS')
        snipeIT_lookup = {'status_id':status_id,
            'model_id': model_id }
    except:
        logging.exception('Failed building lookup')
        return False

def main():
    logging.info('Starting snipe_it_asset_sync')
    successful_lookup = build_snipeIT_lookup()
    if not successful_lookup:
        return
    assets = tio_assets()
    process_assets(assets=assets)
    logging.info('Done snipe_it_asset_sync')

if __name__ == '__main__':
    main()
    print('Done')