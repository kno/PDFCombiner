import gettext
import locale
import os

def setup_gettext():
    """Setup gettext for the application."""
    import os
    import gettext

    # Get language from environment
    lang_env = os.environ.get('LANG', 'es_ES.UTF-8')

    # Extract language code (es, en, etc.)
    lang_code = lang_env.split('_')[0] if '_' in lang_env else lang_env.split('.')[0]

    try:
        # Try to load the specific language
        translation = gettext.translation('messages', localedir='locale', languages=[lang_code])
        translation.install()
        _ = translation.gettext
    except FileNotFoundError:
        # Fallback to English if the specific language is not found
        try:
            translation = gettext.translation('messages', localedir='locale', languages=['en'])
            translation.install()
            _ = translation.gettext
        except FileNotFoundError:
            # Final fallback to no translation
            _ = gettext.gettext

    return _

# Setup gettext automatically when module is imported
_ = setup_gettext()
