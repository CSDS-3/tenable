# need to export compliance audits to splunk
from tenable.io import TenableIO
import arrow
from pathlib import Path
import logging
import json

tio = TenableIO()
logging.basicConfig(level='INFO', format='%(asctime)s - %(levelname)s - %(message)s')

# file that stores the how far to look for findings
CHECKPOINT = Path('audit_checkpoint')
# findings / page
NUM_FINDINGS = 500
# async threads
THREADS = 6

def arrowfy(func):
    def convert(*args, **kwargs):
        result = func(*args, **kwargs)
        return arrow.get(result)
    return convert

@arrowfy
def read_checkpoint(checkpoint=CHECKPOINT):
    logging.info(f'Reading {checkpoint=}')
    if not checkpoint.exists():
        return 0
    return checkpoint.read_text()

def write_chunk(data, export_uuid, export_type, export_chunk_id):
    fn = f'{export_type}-{export_uuid}-{export_chunk_id}.json'
    logging.info(f'Writing Audit export to {fn=}')
    with open(fn,'w') as fobj:
        json.dump(data, fobj)

def export_compliance(checkpoint):
    logging.info(f'Pulling Audits since {checkpoint=}')
    try:
        export = tio.exports.compliance(last_seen=checkpoint.int_timestamp, num_findings=NUM_FINDINGS)
        export.run_threaded(write_chunk, num_threads=THREADS)
    except:
        logging.exception('API Error')
        return False

def write_checkpoint(new_checkpoint):
    logging.info('Writing new checkpoint back')
    logging.debug(f'{new_checkpoint=}')
    CHECKPOINT.write_text(new_checkpoint)

def main():
    logging.info('Begin Audit export')
    checkpoint = read_checkpoint()
    new_checkpoint = arrow.utcnow()
    audit_export = export_compliance(checkpoint=checkpoint)
    if audit_export:
        write_checkpoint(new_checkpoint)
    logging.info('Finished Audit export')
    

if __name__ == "__main__":
    main()
    print('Done')