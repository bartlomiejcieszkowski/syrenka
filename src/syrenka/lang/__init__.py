"""syrenka.lang module"""

import syrenka.lang.base


class LangAnalyst:
    """Class responsible for creating analyst for detected language"""

    @staticmethod
    def create_lang_class(obj):
        """crates lang class for given object if available"""
        for analysis_type in syrenka.lang.base.LANG_ANALYSIS:
            if analysis_type.handles(obj):
                return analysis_type.create_lang_class(obj)

        raise TypeError(f"Unsupported {obj=} of type={type(obj)}")
