from jd.models.result_tag import ResultTag


class TagService:
    StatusMap = {
        ResultTag.StatusType.INVALID: '无效',
        ResultTag.StatusType.VALID: '有效'
    }
