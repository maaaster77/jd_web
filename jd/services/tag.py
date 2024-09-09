from jd.models.result_tag import ResultTag


class TagService:
    StatusMap = {
        ResultTag.StatusType.INVALID: '无效',
        ResultTag.StatusType.VALID: '有效'
    }

    @classmethod
    def list(cls):
        tags = ResultTag.query.filter_by(status=ResultTag.StatusType.VALID).all()
        tag_list = [{
            'id': row.id,
            'name': row.title,
        } for row in tags]

        return tag_list

