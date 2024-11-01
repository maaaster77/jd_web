from jd.tasks.first.send_file_job import send_file_job


class SendTgDataJob:
    def main(self):
        send_file_job()





def run():
    job = SendTgDataJob()
    job.main()
