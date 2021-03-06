"""The base avatar service class implementation."""

from __future__ import unicode_literals

from django.template.loader import render_to_string


class AvatarService(object):
    """A service that provides avatar support.

    At the very least, subclasses must set the :py:attr:`id` and
    :py:attr:`name` attributes, as well as override the
    :py:meth:`get_avatar_urls` method.
    """

    #: The avatar service's ID.
    #:
    #: This must be unique for every avatar service subclass.
    avatar_service_id = None

    #: The avatar service's human-readable name.
    name = None

    #: The template for rendering the avatar as HTML.
    template_name = 'avatars/avatar.html'

    def get_avatar_urls(self, request, user, size):
        """Render the avatar URLs for the given user.

        The result of calls to this method will be cached on the request for
        the specified user, service, and size.

        Args:
            request (django.http.HttpRequest):
                The HTTP request.

            user (django.contrib.auth.models.User):
                The user for whom the avatar URLs are to be retrieved.

            size (int, optional):
                The requested avatar size (height and width) in pixels.

        Returns:
            dict:
                A dictionary mapping resolutions to URLs as
                :py:class:`django.utils.safestring.SafeText` objects
                The dictionary must support at least the following resolutions:

                ``'1x'``:
                    The user's regular avatar.

                ``'2x'``:
                    The user's avatar at twice the resolution.

                ``'3x'``:
                    The user's avatar at three times the resolution.

                Any key except for ``'1x'`` may be ``None``.

                The URLs **must** be safe, or rendering errors will occur.
                Explicitly sanitize them and use
                :py:math:`django.utils.html.mark_safe`.
        """
        if not hasattr(request, '_avatar_cache'):
            request._avatar_cache = {}

        key = (user.pk, self.avatar_service_id, size)

        try:
            urls = request._avatar_cache[key]
        except KeyError:
            urls = self.get_avatar_urls_uncached(request, user, size)
            request._avatar_cache[key] = urls

        return urls

    def get_avatar_urls_uncached(self, request, user, size):
        """Return the avatar URLs for the given user.

        Subclasses must override this to provide the actual URLs.

        Args:
            request (django.http.HttpRequest):
                The HTTP request.

            user (django.contrib.auth.models.User):
                The user for whom the avatar URLs are to be retrieved.

            size (int, optional):
                The requested avatar size (height and width) in pixels.

        Returns:
            dict:
                A dictionary of the URLs for the requested user. The
                dictionary will have the following keys:

                * ``'1x'``: The user's regular avatar.
                * ``'2x'``: The user's avatar at twice the resolution
                  (e.g., for retina displays). This may be ``None``.
                * ``'3x'``: The user's avatar at three times the resolution.
                  This may be ``None``.

                The URLs returned by this function **must** be safe, i.e., they
                should be able to be injected into HTML without being
                sanitized. They should be marked safe explicitly via
                :py:meth:`django.utils.html.mark_safe`.
        """
        raise NotImplementedError(
            '%r must implement get_avatar_urls_uncached().'
            % type(self)
        )

    def render(self, request, user, size):
        """Render a user's avatar to HTML.

        By default, this is rendered with the template specified by the
        :py:attr:`template_name` attribute. This behaviour can be overridden
        by subclasses.

        Args:
            request (django.http.HttpRequest):
                The HTTP request.

            user (django.contrib.auth.models.User):
                The user for whom the avatar is to be rendered.

            size (int):
                The requested avatar size (height and width) in pixels.

        Returns:
            unicode: The rendered avatar HTML.
        """
        return render_to_string(self.template_name, {
            'urls': self.get_avatar_urls(request, user, size),
            'username': user.get_full_name() or user.username,
            'size': size,
        })
