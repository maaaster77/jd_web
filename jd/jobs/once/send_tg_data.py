from jd.tasks.first.send_file_job import send_file_job


class SendTgDataJob:

    def __init__(self, data_type, is_all, start_id, max_id):
        self.data_type = int(data_type)
        self.is_all = int(is_all)
        self.start_id = int(start_id)
        self.max_id = int(max_id)

    def main(self):
        send_file_job(self.data_type, self.is_all, self.start_id, self.max_id)


def run(data_type, is_all, start_id, max_id):
    if not data_type:
        raise ValueError('data type is required')
    if not is_all:
        raise ValueError('is_all is required 1-all 0-yesterday')
    job = SendTgDataJob(data_type, is_all, start_id, max_id)
    job.main()
