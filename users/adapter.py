from django.shortcuts import reverse
from django.http import HttpResponseRedirect
from allauth.account.adapter import DefaultAccountAdapter


class AccountAdapter(DefaultAccountAdapter):

    def pre_login(
        self,
        request,
        user,
        *,
        email_verification,
        signal_kwargs,
        email,
        signup,
        redirect_url
    ):
        if not user.is_active:
            return HttpResponseRedirect(reverse('activate', kwargs={'activation_link': user.activation_link}))
