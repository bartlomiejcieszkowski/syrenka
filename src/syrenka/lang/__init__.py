import syrenka.lang.base


class LangAnalyst:
    @staticmethod
    def create_lang_class(obj):
        for analysis_type in syrenka.lang.base.LANG_ANALYSIS:
            if analysis_type.handles(obj):
                return analysis_type.create_lang_class(obj)

        return None
