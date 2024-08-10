from jd.services.spider.chem960_spider import ChemicalNineSpider
from jd.services.spider.chemical_book import ChemicalBookSpider
from jd.services.spider.guide_spider import GuideChemSpider
from jd.services.spider.huayuan_spider import HuaYuanSpider
from jd.services.spider.mobei_spider import MolbaseSpider


class ChemicalPlatformService:
    PLATFORM_MOLBASE = 1  # 摩贝
    PLATFORM_GUIDECHEM = 2  # 盖德化工
    PLATFORM_CHEMICALBOOK = 3  # chemicalbook
    PLATFORM_CHEMICALNINE = 4  # chemical960
    PLATFORM_HUAYUAN = 5  # 化源

    PLATFORM_MAP = {
        PLATFORM_MOLBASE: '摩贝',
        PLATFORM_GUIDECHEM: '盖德',
        PLATFORM_CHEMICALBOOK: 'chemicalbook',
        PLATFORM_CHEMICALNINE: 'chemical960',
        PLATFORM_HUAYUAN: '化源'
    }

    @classmethod
    def get_engine(cls, platform_id):
        if platform_id == ChemicalPlatformService.PLATFORM_MOLBASE:
            return MolbaseSpider()
        if platform_id == ChemicalPlatformService.PLATFORM_GUIDECHEM:
            return GuideChemSpider()
        if platform_id == ChemicalPlatformService.PLATFORM_CHEMICALBOOK:
            return ChemicalBookSpider()
        if platform_id == ChemicalPlatformService.PLATFORM_CHEMICALNINE:
            return ChemicalNineSpider()
        if platform_id == ChemicalPlatformService.PLATFORM_HUAYUAN:
            return HuaYuanSpider()
