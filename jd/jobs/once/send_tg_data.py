from jd.tasks.first.send_file_job import send_file_job


class SendTgDataJob:

    def __init__(self, data_type, is_all):
        self.data_type = int(data_type)
        self.is_all = int(is_all)

    def main(self):
        send_file_job(self.data_type, self.is_all)


def run(data_type, is_all):
    if not data_type:
        raise ValueError('data type is required')
    if not is_all:
        raise ValueError('is_all is required 1-all 0-yesterday')
    job = SendTgDataJob(data_type, is_all)
    job.main()
