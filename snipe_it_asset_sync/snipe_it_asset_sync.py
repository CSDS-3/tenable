from tenable.io import TenableIO
from pysnipeit import SnipeIT
import logging

snipe = SnipeIT()
tio = TenableIO()
logging.basicConfig(level='INFO', format='%(asctime)s - %(levelname)s - %(message)s')

def force_list_to_str(val):
    '''For some reason tenable will use lists for values that 
    can only ever be a str'''  
    if not val:
        return None  
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
    logging.debug(f'Sending {asset=}')
    result = snipe.assets.update(asset)
    logging.debug(f'SnipeIT asset update {result=}')

def lookup_snipe_it_name(function, name):
    return next((i for i in getattr(snipe,function).list() if i['name']==name), None)

def format_asset(asset):
    ''' The SnipeIT API uses custom fields to enrich data like OS'''
    try:
        ec2_id = force_list_to_str(asset.get('aws_ec2_instance_id'))    
        name = force_list_to_str(asset.get('hostname'))
        os = force_list_to_str(asset.get('operating_system'))
        snipe_asset_id = is_known_asset(asset)
        data = {
            'asset_tag': ec2_id,
            'status_id': snipeIT_lookup['status_id'],
            'model_id': snipeIT_lookup['model_id'],
            'name' : name,
            snipeIT_lookup['model_id'] : os
            }
        if snipe_asset_id:
            data['id'] = id
    except:
        logging.exception(f'Formatting error {asset=}')
    # logging.debug(f'Formatted {asset=} to {data=}')
    return data

def is_known_asset(asset):
    ''' '''
    ec2_id = asset.get('aws_ec2_instance_id')
    if not ec2_id:
        logging.warning(f'No EC2 on this Asset {asset=}')
        return False
    for asset in snipeIT_lookup['assets']:
        if asset.get('asset_tag') == 'ec2_id':
            logging.info('Found existing Snipe_Asset')
            return asset['id']
    logging.info('New SnipeIT Asset')
    
def build_snipeIT_lookup():

    global snipeIT_lookup
    try:
        status_id = lookup_snipe_it_name(function='status_labels', name='Ready to Deploy')['id']
        model_id = lookup_snipe_it_name(function='models', name='AWS EC2')['id']
        os_id = lookup_snipe_it_name(function='fields', name='OS')['db_column_name']
        assets = [{k:v} for k,v in snipe.assets.list().items() if k in ['id','asset_tag']]
        snipeIT_lookup = {'status_id':status_id,
            'model_id': model_id,
             'os_id': os_id,
              'assets': assets }
        return True
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