from jd.services.spider.chemical_book import ChemicalBookSpider
from jd.services.spider.guide_spider import GuideChemSpider
from jd.services.spider.mobei_spider import MolbaseSpider


class ChemicalPlatformService:
    PLATFORM_MOLBASE = 1  # 摩贝
    PLATFORM_GUIDECHEM = 2  # 盖德化工
    PLATFORM_CHEMICALBOOK = 3  # chemicalbook

    PLATFORM_MAP = {
        PLATFORM_MOLBASE: '摩贝',
        PLATFORM_GUIDECHEM: '盖德',
        PLATFORM_CHEMICALBOOK: 'chemicalbook'
    }

    @classmethod
    def get_engine(cls, platform_id):
        if platform_id == ChemicalPlatformService.PLATFORM_MOLBASE:
            return MolbaseSpider()
        if platform_id == ChemicalPlatformService.PLATFORM_GUIDECHEM:
            return GuideChemSpider()
        if platform_id == ChemicalPlatformService.PLATFORM_CHEMICALBOOK:
            return ChemicalBookSpider()
