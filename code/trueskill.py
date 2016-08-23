from math import sqrt
from scipy.special import erfinv
from scipy.special import log_ndtr
from numpy import logaddexp
import math
import scipy.stats
import numpy as np

def logdiffexp(a, b):
  if a == b: return -10000000
  return a + math.log(-np.expm1(b-a))


class TrueSkill:
  def __init__(self, beta2, tau2, prob_draw, var0):
    self.beta2 = beta2 # rating class width
    self.tau2 = tau2 # additive dynamics
    self.draw_margin = TrueSkill.inv_cdf(0.5*(prob_draw + 1.0))*sqrt(2*beta2 + 2*var0) # the draw margin
    #print self.draw_margin
    
  def update_rating(self, winner, loser, isDraw):
    # unpack data
    mu_winner, var_winner = winner
    mu_loser, var_loser = loser

    # before updates perform additive dynamics
    var_winner += self.tau2
    var_loser += self.tau2

    # precompute some values
    c = sqrt(2*self.beta2 + var_winner + var_loser)
    t = (mu_winner - mu_loser)/c
    eps = self.draw_margin/c
    logpdfmm = TrueSkill.logpdf(-eps-t)
    logpdfpp = logpdfmm
    logpdfpm = TrueSkill.logpdf(eps-t)
    logpdfmp = logpdfpm

    logcdfmm = TrueSkill.logcdf(-eps-t)
    logcdfpp = TrueSkill.logcdf(eps+t)
    logcdfpm = TrueSkill.logcdf(eps-t)
    logcdfmp = TrueSkill.logcdf(-eps+t)
    
    if isDraw:
      v = self.v_draw(t, logpdfmm, logpdfpm, logcdfmm, logcdfpm, logpdfmp, logpdfpp, logcdfmp, logcdfpp)
      w = self.w_draw(t, eps, logpdfmm, logpdfpm, logcdfmm, logcdfpm, logpdfmp, logpdfpp, logcdfmp, logcdfpp)
    else:
      v = self.v_nondraw(logpdfmp, logcdfmp)
      w = self.w_nondraw(t, eps, logpdfmp, logcdfmp)

    mu_winner += var_winner*v/c
    mu_loser -= var_loser*v/c
    var_winner *= (1.0 - var_winner*w/(c**2))
    var_loser *= (1.0 - var_loser*w/(c**2))
    if var_winner < 0 or var_loser < 0: print(mu_winner, mu_loser)
    return ((mu_winner, var_winner), (mu_loser, var_loser))

  @staticmethod
  def inv_cdf(prob):
    return sqrt(2.0)*erfinv(2*prob - 1.0)

  
  @staticmethod
  def logpdf(x):
    return 0.5*(-x**2 - math.log(2*math.pi))

  @staticmethod
  def logcdf(x):
    #if x > 0: return math.log1p(-math.exp(TrueSkill.logcdf(-x)))  
    return log_ndtr(x)
    
  
  @staticmethod
  def v_nondraw(logpdfmp, logcdfmp):
    return math.exp(logpdfmp - logcdfmp)

  @staticmethod
  def v_draw(t, logpdfmm, logpdfpm, logcdfmm, logcdfpm, logpdfmp, logpdfpp, logcdfmp, logcdfpp):
    if t<0: return -TrueSkill.v_draw(-t, logpdfmp, logpdfpp, logcdfmp, logcdfpp, logpdfmm, logpdfpm, logcdfmm, logcdfpm)
    mul = 1.0
    if logpdfmm < logpdfpm:
      logpdfmm, logpdfpm = logpdfpm, logpdfmm
      mul = -mul
    if logcdfpm < logcdfmm:
      logcdfpm, logcdfmm = logcdfmm, logcdfpm
      mul = -mul
    return mul*math.exp(logdiffexp(logpdfmm, logpdfpm) - logdiffexp(logcdfpm, logcdfmm))

  @staticmethod
  def w_nondraw(t, eps, logpdfmp, logcdfmp):
    vnondraw = TrueSkill.v_nondraw(logpdfmp, logcdfmp)
    return vnondraw*(vnondraw + t - eps)

  @staticmethod
  def w_draw(t, eps, logpdfmm, logpdfpm, logcdfmm, logcdfpm, logpdfmp, logpdfpp, logcdfmp, logcdfpp):
    if t < 0: return TrueSkill.w_draw(-t, eps, logpdfmp, logpdfpp, logcdfmp, logcdfpp, logpdfmm, logpdfpm, logcdfmm, logcdfpm)
    sign = 1.0
    if eps - t > 0:
      logpm = math.log(eps - t)
    else:
      logpm = math.log(t-eps)
      sign = -sign
    logpp = math.log(eps + t)
    if sign == 1: loga = logaddexp(logpm + logpdfpm, logpp + logpdfpp)
    else:
      if logpm + logpdfpm > logpp + logpdfpp:
        loga = logdiffexp(logpm + logpdfpm, logpp + logpdfpp)
        sign = -1.0
      else:
        loga = logdiffexp(logpp + logpdfpp, logpm + logpdfpm)
        sign = 1.0
    logb = logdiffexp(logcdfpm, logcdfmm)
    vdraw = TrueSkill.v_draw(t, logpdfmm, logpdfpm, logcdfmm, logcdfpm, logpdfmp, logpdfpp, logcdfmp, logcdfpp)
    return vdraw**2  + sign*math.exp(loga - logb)


def precompute(eps, t):
  logpdfmm = TrueSkill.logpdf(-eps-t)
  logpdfpp = logpdfmm
  logpdfpm = TrueSkill.logpdf(eps-t)
  logpdfmp = logpdfpm

  logcdfmm = TrueSkill.logcdf(-eps-t)
  logcdfpp = TrueSkill.logcdf(eps+t)
  logcdfpm = TrueSkill.logcdf(eps-t)
  logcdfmp = TrueSkill.logcdf(-eps+t)
  return logpdfmm, logpdfpp, logpdfpm, logpdfmp, logcdfmm, logcdfpp, logcdfpm, logcdfmp

'''
from pylab import *
import numpy as np
x = np.linspace(-50,50,1000)

epss = (0.0001,0.1,1, 4, 10)
subplot(2,2,1)
for eps in epss:
  y = []
  for t in x:
    logpdfmm, logpdfpp, logpdfpm, logpdfmp, logcdfmm, logcdfpp, logcdfpm, logcdfmp = precompute(eps, t)
    #if cdfmp == 0: cdfmp = 1E-17
    y.append(TrueSkill.v_nondraw(logpdfmp, logcdfmp))
  plot(x,y)

subplot(2,2,2)
for eps in epss:
  y = []
  for t in x:
    logpdfmm, logpdfpp, logpdfpm, logpdfmp, logcdfmm, logcdfpp, logcdfpm, logcdfmp = precompute(eps, t)
    y.append(TrueSkill.v_draw(t, logpdfmm, logpdfpm, logcdfmm, logcdfpm, logpdfmp, logpdfpp, logcdfmp, logcdfpp))
  plot(x,y)

subplot(2,2,3)
for eps in epss:
  y = []
  for t in x:
    logpdfmm, logpdfpp, logpdfpm, logpdfmp, logcdfmm, logcdfpp, logcdfpm, logcdfmp = precompute(eps, t)
    y.append(TrueSkill.w_nondraw(t, eps, logpdfmp, logcdfmp))
  plot(x,y)

subplot(2,2,4)
for eps in epss:
  y = []
  for t in x:
    logpdfmm, logpdfpp, logpdfpm, logpdfmp, logcdfmm, logcdfpp, logcdfpm, logcdfmp = precompute(eps, t)
    y.append(TrueSkill.w_draw(t, eps, logpdfmm, logpdfpm, logcdfmm, logcdfpm, logpdfmp, logpdfpp, logcdfmp, logcdfpp))
  plot(x,y)

show()

# testing TrueSkill with recommended values
mu0 = 25.0
var0 = (mu0/3.0)**2
beta2 = var0/4.0
tau2 = var0*100
prob_draw = 0.1
ts = TrueSkill(beta2, tau2, prob_draw, var0)
#ts = TrueSkill(1,0,0)
mu1, var1, mu2, var2 = 25, 8, 20, 5
print ts.update_rating((mu1, var1), (mu2, var2), False)
print ts.update_rating((mu2, var2), (mu1, var1), False)
print ts.update_rating((mu1, var1), (mu2, var2), True)
#for i in xrange(100):
#  print i, mu1, var1, mu2, var2
#  mu1, var1, mu2, var2 = ts.update_rating(mu1, var1, mu2, var2, True)
'''
