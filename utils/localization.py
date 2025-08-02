import gettext
import locale
import os

# Global translation object
_current_translation = None

def setup_gettext():
    """Setup gettext for the application."""
    global _current_translation
    import os
    import gettext
    import builtins
    # Get language from environment
    lang_env = os.environ.get('LANG', 'es_ES.UTF-8')
    # Extract language code (es, en, etc.)
    lang_code = lang_env.split('_')[0] if '_' in lang_env else lang_env.split('.')[0]
    # Use absolute path for locale dir
    locale_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'locale')
    locale_dir = os.path.abspath(locale_dir)
    try:
        # Try to load the specific language
        translation = gettext.translation('messages', localedir=locale_dir, languages=[lang_code])
        translation.install()
        _current_translation = translation
    except FileNotFoundError:
        # Fallback to English if the specific language is not found
        try:
            translation = gettext.translation('messages', localedir=locale_dir, languages=['en'])
            translation.install()
            _current_translation = translation
        except FileNotFoundError:
            # Final fallback to no translation
            _current_translation = gettext

    def _translate(message):
        if _current_translation:
            return _current_translation.gettext(message)
        return message

    builtins._ = _translate
    return _translate

def get_text(message):
    """Get translated text - always uses current translation"""
    if _current_translation:
        return _current_translation.gettext(message)
    return message

# Setup gettext automatically when module is imported
_ = setup_gettext()
