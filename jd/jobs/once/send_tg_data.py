from jd.tasks.first.send_file_job import send_file_job


class SendTgDataJob:

    def __init__(self, data_type):
        self.data_type = int(data_type)

    def main(self):
        send_file_job(self.data_type)


def run(data_type):
    if not data_type:
        raise ValueError('data type is required')
    job = SendTgDataJob(data_type)
    job.main()
