import random
import math
from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from facemash.models import FaceMash


def play(request):
    """ The main-page view of facemash app. """
    try:
        contestants = FaceMash.objects.all()
        contestant_1 = random.choice(contestants)
        contestant_2 = random.choice(contestants)
        # A while loop to ensure that the contestants aren't same.
        while contestant_1 == contestant_2:
            contestant_2 = random.choice(contestants)
        args = {'contestant_1': contestant_1, 'contestant_2': contestant_2}
    except IndexError:
        error = True
        args = {'error': error}
    return render(request, 'facemash.html', args) 

def ratings_calculator(request, winner_id, loser_id):
    """
    This view is the HEART of facemash app. This is where all the calculations
    for the ratings are done. This is where the algorithm is.
    """
    try:
        winner = FaceMash.objects.get(id=winner_id)
        loser = FaceMash.objects.get(id=loser_id)
        w = winner
        l = loser

        TAU = 0.5 # System constant
        # score = s
        s_w = 1.0
        s_l = 0.0
        # mu
        mu_w = (w.ratings - 1500.0)/173.7178
        mu_l = (l.ratings - 1500.0)/173.7178
        # phi
        phi_w = w.rd/173.7178
        phi_l = l.rd/173.7178
        # g(phi) = g
        g_w = 1.0/math.sqrt(1.0 + 3.0*pow(phi_w, 2)/pow(math.pi, 2))
        g_l = 1.0/math.sqrt(1.0 + 3.0*pow(phi_l, 2)/pow(math.pi, 2))
        # E = E
        E_w = 1.0/(1.0 + math.exp(-g_w*(mu_w - mu_l)))
        E_l = 1.0/(1.0 + math.exp(-g_l*(mu_l - mu_w)))
        # nu
        nu_w = 1.0/(pow(g_l, 2)*E_w*(1 - E_w))
        nu_l = 1.0/(pow(g_w, 2)*E_l*(1 - E_l))
        # delta = delta
        delta_w = nu_w*g_l*(s_w - E_w) # s_w = 1
        delta_l = nu_l*g_w*(s_l - E_l) # s_l = 0
        # a = a
        a_w = math.log(pow(w.sigma, 2), math.e)
        a_l = math.log(pow(l.sigma, 2), math.e)

        # f(x) = function_x
        def function_x(x, delta, phi, nu, a):
            """
            This function corresponds to f(x) in Glicko-2 Algorithm.
            """

            e_x = math.exp(x)
            multi = pow(delta, 2) - pow(phi, 2) - nu - math.exp(x)
            divi = 2.0*pow((phi+nu+e_x), 2)
            minus = (x-a)/pow(TAU, 2)
            result = e_x*multi/divi - minus
            return result

        EPSILON = 0.000001 # Convergence tolerance
        # Calculate for w (winner).
        A_w = a_w
        if pow(delta_w, 2) > (pow(phi_w, 2) + nu_w):
            B_w = math.log((pow(delta_w, 2) - pow(phi_w, 2) - nu_w), math.e)
        else:
            k = 1
            x = a_w - k*TAU
            f_x = function_x(x, delta_w, phi_w, nu_w, a_w)
            while f_x < 0:
                k += 1
                x = a_w - k*TAU
                function_x(x, delta_w, phi_w, nu_w, a_w)
            B_w = a_w - k*TAU

        # find f(A_w)
        f_A_w = function_x(A_w, delta_w, phi_w, nu_w, a_w)
        # find f(B_w)
        f_B_w = function_x(B_w, delta_w, phi_w, nu_w, a_w)

        while abs(B_w - A_w) > EPSILON:
            C_w = A_w + (A_w-B_w)*f_A_w/(f_B_w-f_A_w)
            # find f(C_w)
            f_C_w = function_x(C_w, delta_w, phi_w, nu_w, a_w)
            if f_C_w*f_B_w < 0:
                A_w = B_w
                f_A_w = f_B_w
            else:
                f_A_w = f_A_w/2.0
            B_w = C_w
            f_B_w = f_C_w
        # sigmama-dash = sigma_2
        sigma_2_w = math.exp(A_w/2.0)
        # phi-star = p_s
        p_s_w = math.sqrt(pow(phi_w, 2)+pow(sigma_2_w, 2))
        # calculate for l (loser)
        A_l = a_l
        if pow(delta_l, 2) > (pow(phi_l, 2) + nu_l):
            B_l = math.log((pow(delta_l, 2) - pow(phi_l, 2) - nu_l), math.e)
        else:
            k = 1
            x = a_l - k*TAU
            f_x = function_x(x, delta_l, phi_l, nu_l, a_l)
            while f_x < 0:
                k += 1
                x = a_l - k*TAU
                function_x(x, delta_l, phi_l, nu_l, a_l)
            B_l = a_l - k*TAU
        # find f(A_l)
        f_A_l = function_x(A_l, delta_l, phi_l, nu_l, a_l)
        # find f(B_l)
        f_B_l = function_x(B_l, delta_l, phi_l, nu_l, a_l)
        while abs(B_l - A_l) > EPSILON:
            C_l = A_l + (A_l-B_l)*f_A_l/(f_B_l-f_A_l)
            # find f(C_l)
            f_C_l = function_x(C_l, delta_l, phi_l, nu_l, a_l)
            if f_C_l*f_B_l < 0:
                A_l = B_l
                f_A_l = f_B_l
            else:
                f_A_l = f_A_l/2.0
            B_l = C_l
            f_B_l = f_C_l
        # sigmama-dash = sigma_2
        sigma_2_l = math.exp(A_l/2.0)
        # phi-star = p_s
        p_s_l = math.sqrt(pow(phi_l, 2)+pow(sigma_2_l, 2))
        # phi-dash = p_2
        p_2_w = 1.0/math.sqrt(1.0/pow(p_s_w, 2) + 1.0/nu_w)
        p_2_l = 1.0/math.sqrt(1.0/pow(p_s_l, 2) + 1.0/nu_l)
        # mu-dash = u_2
        u_2_w = mu_w + pow(p_s_w, 2)*g_l*(s_w - E_w)
        u_2_l = mu_l + pow(p_s_l, 2)*g_w*(s_l - E_l)
        # convert back to orignial ratings
        w.ratings = 173.7178*u_2_w + 1500
        w.sigma = sigma_2_w
        l.ratings = 173.7178*u_2_l + 1500
        l.sigma = sigma_2_l

        # As pointed out by the author of Glicko-2, rd (rating deviation)
        # should not go below 30.
        # Therefore, below make a check for that.

        w.rd = 173.7178*p_2_w # New rd of winner
        if w.rd < 30:
            w.rd = 30
        l.rd = 173.7178*p_2_l # New rd of loser
        if l.rd < 30:
            l.rd = 30
        # Save the new ratings, rd and volatality for both winner and loser.
        w.save()
        l.save()
        # Redirect back to the Play page
        return HttpResponseRedirect('/facemash/')
    except FaceMash.DoesNotExist:
        raise Http404


def ratings_page(request):
    """ The ratings-page view. """

    faces = FaceMash.objects.all().order_by('-ratings')
    return render(request, "ratings_page.html", {'faces' : faces})

