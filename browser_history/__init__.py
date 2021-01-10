import inspect
import webbrowser

from . import browsers, generic, utils  # noqa: F401


__version__ = "0.3.0"


def get_browsers():
    """This method provides a list of all browsers implemented by
    browser_history.

    :return: A :py:class:`list` containing implemented browser classes
        all inheriting from the super class
        :py:class:`browser_history.generic.Browser`

    :rtype: :py:class:`list`
    """

    # recursively get all concrete subclasses
    def get_subclasses(browser):
        # include browser itself in return list if it is concrete
        sub_classes = []
        if not inspect.isabstract(browser):
            sub_classes.append(browser)

        for sub_class in browser.__subclasses__():
            sub_classes.extend(get_subclasses(sub_class))
        return sub_classes

    return get_subclasses(generic.Browser)


def get_history():
    """This method is used to obtain browser histories of all available and
    supported browsers for the system platform.

    :return: Object of class :py:class:`browser_history.generic.Outputs` with
        the data member histories set to
        list(tuple(:py:class:`datetime.datetime`, str))

    :rtype: :py:class:`browser_history.generic.Outputs`
    """
    output_object = generic.Outputs(fetch_type="history")
    browser_classes = get_browsers()
    for browser_class in browser_classes:
        try:
            browser_object = browser_class()
            browser_output_object = browser_object.fetch_history()
            output_object.histories.extend(browser_output_object.histories)
        except AssertionError:
            utils.logger.info("%s browser is not supported", browser_class.name)
    output_object.histories.sort()
    return output_object


def get_bookmarks():
    """This method is used to obtain browser bookmarks of all available and
    supported browsers for the system platform.

    :return: Object of class :py:class:`browser_history.generic.Outputs` with
        the data member bookmarks set to
        list(tuple(:py:class:`datetime.datetime`, str, str, str))

    :rtype: :py:class:`browser_history.generic.Outputs`
    """
    output_object = generic.Outputs(fetch_type="bookmarks")
    subclasses = get_browsers()
    for browser_class in subclasses:
        try:
            browser_object = browser_class()
            assert (
                browser_object.bookmarks_file is not None
            ), f"Bookmarks are not supported on {browser_class.name}"
            browser_output_object = browser_object.fetch_bookmarks()
            output_object.bookmarks.extend(browser_output_object.bookmarks)
        except AssertionError as e:
            utils.logger.info("%s", e)
    output_object.bookmarks.sort()
    return output_object


# keep everything lower-cased
browser_aliases = {
    "google-chrome": "chrome",
    "chromehtml": "chrome",
    "chromium-browser": "chromium",
    "msedgehtm": "edge",
    "operastable": "opera",
    "firefoxurl": "firefox",
}


def default_browser():
    plat = utils.get_platform()

    if plat == utils.Platform.LINUX:
        default = webbrowser.get().name.lower()
    else:
        utils.logger.info("Default browser feature not supported on this OS")
        return None

    if default in [browser.__name__.lower() for browser in get_browsers()]:
        # we are lucky and the name is exactly like we want it
        return default
    elif default in browser_aliases:
        # check if it matches any aliases
        return browser_aliases[default]
    else:
        utils.logger.info("Current default browser is not supported")
