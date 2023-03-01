# need to export compliance audits to splunk
from tenable.io import TenableIO
import arrow
from pathlib import Path
import logging
import json
import logging_utils

tio = TenableIO()
logger = logging_utils.get_logger(logger_name='tio_compliance', log_folder=".")

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
    logger.info(f'Reading {checkpoint=}')
    if not checkpoint.exists():
        return 0
    return checkpoint.read_text()

def write_chunk(data, export_uuid, export_type, export_chunk_id):
    fn = f'{export_type}-{export_uuid}-{export_chunk_id}.json'
    logger.info(f'Writing Audit export to {fn=}')
    with open(fn,'w') as fobj:
        json.dump(data, fobj)

def export_compliance(checkpoint):
    logger.info(f'Pulling Audits since {checkpoint=}')
    try:
        export = tio.exports.compliance(last_seen=checkpoint.int_timestamp, num_findings=NUM_FINDINGS)
        export.run_threaded(write_chunk, num_threads=THREADS)
    except:
        logger.exception('API Error')
        return False
    return True

def write_checkpoint(new_checkpoint):
    logger.info('Writing new checkpoint back')
    logger.debug(f'{new_checkpoint=}')
    CHECKPOINT.write_text(str(new_checkpoint))

def main():
    logger.info('Begin Audit export')
    checkpoint = read_checkpoint()
    new_checkpoint = arrow.utcnow()
    audit_export = export_compliance(checkpoint=checkpoint)
    if audit_export:
        write_checkpoint(new_checkpoint)
    logger.info('Finished Audit export')
    

if __name__ == "__main__":
    main()
    print('Done')