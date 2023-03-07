# launches scans against all assets in SnipeIT


from tenable.io import TenableIO
from pysnipeit import SnipeIT
import logging
import sys
sys.path.append('../tools')
import logging_utils

snipe = SnipeIT()
tio = TenableIO()
logger = logging_utils.get_logger(logger_name='scan_enforce')

SCAN_NAME = 'AutoScan'

def get_snipe_assets():
    try:
        return snipe.assets.list()
    except:
        logger.exception('Could not retrieve snipe_IT assets')

def filter_snipe_to_ip(assets):
    ips = []
    for asset in assets:
        if not asset.get('custom_fields'):
            continue
        for custom_field,values in asset['custom_fields'].items():
            if custom_field == 'ip':
                ips.append(values['value'])
    return ips

def get_scan(name):
    return next(i for i in tio.scans.list() if i['name'].lower()==name.lower())

def scan_target(targets, scan):
    if not targets:
        logger.info('No Targets to scan')
    try:
        tio.scans.launch(scan_id=scan, targets=targets)
    except:
        logger.exception('Failure launching scan')
    

def main():
    logger.info('Starting scan_enforce')
    assets = get_snipe_assets()
    if not assets:
        return
    targets = filter_snipe_to_ip(assets=assets)
    scan = get_scan(SCAN_NAME)
    scan_target(targets=targets, scan=scan['id'])
    logger.info('Done scan_enforce')

if __name__ == '__main__':
    main()
    print('Done')