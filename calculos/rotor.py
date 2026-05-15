import numpy as np
from barril.units import Scalar, Array

g = Scalar(9.81, 'm/s2')
rho = Scalar(1000, 'kg/m3')

def Calcular_Y(H):
    return H * g

tabela_Ns = [
  {"tipo": "Turbina hidráulica Pelton", "Ns_min": 5, "Ns_max": 70},
  {"tipo": "Turbina hidráulica Francis lenta", "Ns_min": 50, "Ns_max": 120},
  {"tipo": "Turbina hidráulica Francis normal", "Ns_min": 120, "Ns_max": 200},
  {"tipo": "Turbina hidráulica Francis rápida", "Ns_min": 200, "Ns_max": 320},
  {"tipo": "Turbina hidráulica Michell-Banki", "Ns_min": 30, "Ns_max": 210},
  {"tipo": "Turbina hidráulica Dériaz", "Ns_min": 200, "Ns_max": 450},
  {"tipo": "Turbina hidráulica Kaplan ou Hélice", "Ns_min": 300, "Ns_max": 1000},
  {"tipo": "Turbina a vapor ou a gás com admissão parcial", "Ns_min": 6, "Ns_max": 30},
  {"tipo": "Turbina a vapor ou a gás com admissão total", "Ns_min": 30, "Ns_max": 300},
  {"tipo": "Bomba de deslocamento positivo", "Ns_min": None, "Ns_max": 30},
  {"tipo": "Bomba centrífuga", "Ns_min": 30, "Ns_max": 250},
  {"tipo": "Bomba semi-axial ou de fluxo misto", "Ns_min": 250, "Ns_max": 450},
  {"tipo": "Bomba axial", "Ns_min": 450, "Ns_max": 1000},
  {"tipo": "Compressor de deslocamento positivo", "Ns_min": None, "Ns_max": 20},
  {"tipo": "Ventilador ou turbocompressor centrífugo", "Ns_min": 20, "Ns_max": 330},
  {"tipo": "Ventilador ou turbocompressor axial", "Ns_min": 330, "Ns_max": 1800}
]

Ns_ref_eta_h = np.array([40., 150.], np.float64)
eta_h_ref = np.array([0.70, 0.90], np.float64)

Ns_ref_eta_a = np.array([60., 180., 350.], np.float64)
eta_a_ref = np.array([0.93, 0.98, 0.99], np.float64)

def Calcular_Ns(V_dot, Y, N):
  Ns = 1e3 * N.GetValue('rev/s') * V_dot.GetValue('m3/s')**(1/2) / Y.GetValue()**(3/4)
  return Scalar(Ns, 'unitless')

def Classificar_Ns(Ns):
  Ns_valor = Ns.GetValue('unitless')
  classificacoes = []

  for item in tabela_Ns:
    Ns_min = item["Ns_min"]
    Ns_max = item["Ns_max"]

    if Ns_min is None and Ns_valor < Ns_max:
      classificacoes.append(item["tipo"])
    elif Ns_min is not None and Ns_min <= Ns_valor <= Ns_max:
      classificacoes.append(item["tipo"])

  return classificacoes

def Calcular_Rendimentos(Ns, configuracao_rotor):
  configuracao_rotor = configuracao_rotor.lower()

  if configuracao_rotor not in ['aberto', 'fechado']:
    raise ValueError("configuracao_rotor deve ser 'aberto' ou 'fechado'.")

  eta_h = np.interp(Ns.GetValue('unitless'), Ns_ref_eta_h, eta_h_ref)
  eta_a = 1.00 if configuracao_rotor == 'aberto' else np.interp(Ns.GetValue('unitless'), Ns_ref_eta_a, eta_a_ref)
  eta_m = (0.96 + 0.99) / 2
  eta_v = (0.90 + 0.98) / 2

  return Scalar(eta_h, 'unitless'), Scalar(eta_a, 'unitless'), Scalar(eta_m, 'unitless'), Scalar(eta_v, 'unitless')

def Calcular_W_acio(rho, V_dot, H, g, eta_h, eta_v, eta_a, eta_m):
  eta_t = eta_h.GetValue('unitless') * eta_v.GetValue('unitless') * eta_a.GetValue('unitless') * eta_m.GetValue('unitless')
  W_acio = (rho.GetValue('kg/m3') * V_dot.GetValue('m3/s') * g.GetValue('m/s2') * H.GetValue('m')) / eta_t
  return Scalar(W_acio, 'W'), Scalar(eta_t, 'unitless')

def Calcular_d_e(W_acio, N, K_e):
  d_e = K_e.GetValue('unitless') * (W_acio.GetValue('kW') / N.GetValue('rpm'))**(1/3)
  return Scalar(d_e, 'cm')

def Calcular_d_e(W_acio, N, numero_estagios):
  if numero_estagios == "um":
    K_e = 14
  elif numero_estagios == "varios":
    K_e = 16
  else:
    raise ValueError("Use 'um' para bomba de um estágio ou 'varios' para bomba de vários estágios.")

  d_e = K_e * (W_acio.GetValue('kW') / N.GetValue('rpm'))**(1/3)
  return Scalar(d_e, 'cm')

def Calcular_Va(Ns, Y):
  K_Va = 6.84e-3 * Ns.GetValue('unitless')**(2/3)
  Va = K_Va * np.sqrt(2 * Y.GetValue())
  return Scalar(Va, 'm/s'), Scalar(K_Va, 'unitless')

def Calcular_Da(V_dot, Va, eta_v, d_e):
  d_c = d_e.GetValue('m') + Scalar(20, 'mm').GetValue('m')
  D_a = np.sqrt((4 * V_dot.GetValue('m3/s')) / (np.pi * Va.GetValue('m/s') * eta_v.GetValue('unitless'))) + d_c
  return Scalar(D_a, 'm'), Scalar(d_c, 'm')

def Calcular_Psi_U5_R5(Ns, Y, N):
  Psi = 1.1424 - 0.0016 * Ns.GetValue('unitless')
  U5 = np.sqrt((2 * Y.GetValue()) / Psi)
  R5 = U5 / N.GetValue('rad/s')
  beta_5 = Scalar(30, 'dega')
  return Scalar(Psi, 'unitless'), Scalar(U5, 'm/s'), Scalar(R5, 'm'), beta_5

def Calcular_R4_Vn3_b4(Ns, R5, V_dot, eta_v, Va):
  relacao_R4_R5 = 0.044 * Ns.GetValue('unitless')**(1/2)
  R4 = relacao_R4_R5 * R5.GetValue('m')
  V_n3 = 1.03 * Va.GetValue('m/s')
  b4 = V_dot.GetValue('m3/s') / (eta_v.GetValue('unitless') * np.pi * (2 * R4) * V_n3)
  return Scalar(relacao_R4_R5, 'unitless'), Scalar(R4, 'm'), Scalar(V_n3, 'm/s'), Scalar(b4, 'm')

def Calcular_R4_Vn3_b4_V4_beta4(Ns, R5, V_dot, eta_v, Va, N):
  relacao_R4_R5 = 0.044 * Ns.GetValue('unitless')**(1/2)
  R4 = relacao_R4_R5 * R5.GetValue('m')
  V_n3 = 1.03 * Va.GetValue('m/s')
  b4 = V_dot.GetValue('m3/s') / (eta_v.GetValue('unitless') * np.pi * (2 * R4) * V_n3)
  f_e4 = 0.85
  V4 = V_n3 / f_e4
  U4 = N.GetValue('rad/s') * R4
  beta4 = np.arctan(V4 / U4)
  return Scalar(relacao_R4_R5, 'unitless'), Scalar(R4, 'm'), Scalar(V_n3, 'm/s'), Scalar(b4, 'm'), Scalar(f_e4, 'unitless'), Scalar(V4, 'm/s'), Scalar(U4, 'm/s'), Scalar(beta4, 'rad')

def Calcular_Numero_Pas(R5, R4, beta_5, beta4, tipo_rotor):
  if tipo_rotor == "fundido":
    K_N = 6.5
    N_pas = K_N * ((R5.GetValue('m') + R4.GetValue('m')) / (R5.GetValue('m') - R4.GetValue('m'))) * np.sin((beta_5.GetValue('rad') + beta4.GetValue('rad')) / 2)
    N_pas_adotado = np.floor(N_pas)
  elif tipo_rotor == "usinado":
    K_N = 8.0
    N_pas = K_N * ((R5.GetValue('m') + R4.GetValue('m')) / (R5.GetValue('m') - R4.GetValue('m'))) * np.sin((beta_5.GetValue('rad') + beta4.GetValue('rad')) / 2)
    N_pas_adotado = np.ceil(N_pas)
  else:
    raise ValueError("Use 'fundido' ou 'usinado' para definir o tipo de rotor.")

  return Scalar(N_pas, 'unitless'), Scalar(N_pas_adotado, 'unitless')

def Calcular_Vn5_b5(Ns, U5, V_dot, eta_v, R5):
  f_e5 = 1
  V_n5 = 0.0135 * U5.GetValue('m/s') * Ns.GetValue('unitless')**(1/2)
  D5 = 2 * R5.GetValue('m')
  b5 = V_dot.GetValue('m3/s') / (eta_v.GetValue('unitless') * np.pi * D5 * V_n5 * f_e5)
  return Scalar(V_n5, 'm/s'), Scalar(D5, 'm'), Scalar(f_e5, 'unitless'), Scalar(b5, 'm')

def Calcular_e(D5, b5):
  e = 0.3 * (D5.GetValue('mm') * b5.GetValue('mm'))**(1/3)
  return Scalar(e, 'mm')

def Calcular_fe4_beta4_atualizado(R4, e, beta4, N_pas_adotado, V_n3, U4):
  D4 = 2 * R4.GetValue('mm')
  t4 = (np.pi * D4) / N_pas_adotado.GetValue('unitless')
  e_t4 = e.GetValue('mm') / np.sin(beta4.GetValue('rad'))
  f_e4 = (t4 - e_t4) / t4
  V4_atualizado = V_n3.GetValue('m/s') / f_e4
  beta4_atualizado = np.arctan(V4_atualizado / U4.GetValue('m/s'))
  return Scalar(D4, 'mm'), Scalar(t4, 'mm'), Scalar(e_t4, 'mm'), Scalar(f_e4, 'unitless'), Scalar(V4_atualizado, 'm/s'), Scalar(beta4_atualizado, 'rad')

def Calcular_mu(R5, R4, beta_5, N_pas_adotado, tipo_difusor):
  beta_5_graus = beta_5.GetValue('dega')
  beta_5_rad = beta_5.GetValue('rad')
  S_f = (R5.GetValue('m')**2 - R4.GetValue('m')**2) / 2

  if tipo_difusor == "pas_guias":
    fator_Kp = 0.60
  elif tipo_difusor == "voluta":
    fator_Kp = (0.65 + 0.75) / 2
  elif tipo_difusor == "aberto":
    fator_Kp = (0.85 + 1.00) / 2
  else:
    raise ValueError("Use 'pas_guias', 'voluta' ou 'aberto' para definir o tipo de difusor.")

  K_p = fator_Kp * ((1 + beta_5_graus / 60) / (np.pi * np.sin(beta_5_rad)))
  mu = 1 / (1 + K_p * (np.pi / N_pas_adotado.GetValue('unitless')) * (R5.GetValue('m')**2 / S_f) * np.sin(beta_5_rad))

  return Scalar(S_f, 'm2'), Scalar(K_p, 'unitless'), Scalar(mu, 'unitless')

def Calcular_Y_pa_inf(Y, eta_h, mu):
  Y_pa = Scalar(Y.GetValue() / eta_h.GetValue('unitless'), 'J/kg')
  a = Scalar(1 / mu.GetValue('unitless'), 'unitless')
  Y_pa_inf = Scalar(a.GetValue('unitless') * Y_pa.GetValue('J/kg'), 'J/kg')
  return Y_pa, a, Y_pa_inf

def Calcular_U5_atualizado(V_n5, beta_5, Y_pa_inf):
  cotg_beta5 = 1 / np.tan(beta_5.GetValue('rad'))
  U5_atualizado = (V_n5.GetValue('m/s') * cotg_beta5 + np.sqrt((V_n5.GetValue('m/s') * cotg_beta5)**2 + 4 * Y_pa_inf.GetValue('J/kg'))) / 2
  return Scalar(U5_atualizado, 'm/s')

def Calcular_R5_b5_atualizados(U5_atualizado, N, V_dot, eta_v, V_n5, f_e5):
  R5_atualizado = U5_atualizado.GetValue('m/s') / N.GetValue('rad/s')
  D5_atualizado = 2 * R5_atualizado
  b5_atualizado = V_dot.GetValue('m3/s') / (eta_v.GetValue('unitless') * np.pi * D5_atualizado * V_n5.GetValue('m/s') * f_e5.GetValue('unitless'))
  return Scalar(R5_atualizado, 'm'), Scalar(D5_atualizado, 'm'), Scalar(b5_atualizado, 'm')

def Calcular_U6_Vt6(U5_atualizado, V_n5, beta_5, f_e5, mu):
  V_t5 = U5_atualizado.GetValue('m/s') - V_n5.GetValue('m/s') / np.tan(beta_5.GetValue('rad'))
  U6 = U5_atualizado.GetValue('m/s') * f_e5.GetValue('unitless')
  V_t6 = mu.GetValue('unitless') * V_t5
  return Scalar(V_t5, 'm/s'), Scalar(U6, 'm/s'), Scalar(V_t6, 'm/s')


def calcular_rotor(V_dot, H, N, configuracao_rotor, Estagios, tipo_rotor, tipo_difusor):
    Y = Calcular_Y(H)
    Ns = Calcular_Ns(V_dot, Y, N)
    classificacoes = Classificar_Ns(Ns)
    eta_h, eta_a, eta_m, eta_v = Calcular_Rendimentos(Ns, configuracao_rotor)
    W_acio, eta_t = Calcular_W_acio(rho, V_dot, H, g, eta_h, eta_v, eta_a, eta_m)
    d_e = Calcular_d_e(W_acio, N, Estagios)
    Va, K_Va = Calcular_Va(Ns, Y)
    D_a, d_c = Calcular_Da(V_dot, Va, eta_v, d_e)
    Psi, U5, R5, beta_5 = Calcular_Psi_U5_R5(Ns, Y, N)
    relacao_R4_R5, R4, V_n3, b4, f_e4, V4, U4, beta4 = Calcular_R4_Vn3_b4_V4_beta4(Ns, R5, V_dot, eta_v, Va, N)
    N_pas, N_pas_adotado = Calcular_Numero_Pas(R5, R4, beta_5, beta4, tipo_rotor)
    V_n5, D5, f_e5, b5 = Calcular_Vn5_b5(Ns, U5, V_dot, eta_v, R5)
    e = Calcular_e(D5, b5)
    D4, t4, e_t4, f_e4_calculado, V4_atualizado, beta4_atualizado = Calcular_fe4_beta4_atualizado(R4, e, beta4, N_pas_adotado, V_n3, U4)
    S_f, K_p, mu = Calcular_mu(R5, R4, beta_5, N_pas_adotado, tipo_difusor)
    Y_pa, a, Y_pa_inf = Calcular_Y_pa_inf(Y, eta_h, mu)
    U5_atualizado = Calcular_U5_atualizado(V_n5, beta_5, Y_pa_inf)
    R5_atualizado, D5_atualizado, b5_atualizado = Calcular_R5_b5_atualizados(U5_atualizado, N, V_dot, eta_v, V_n5, f_e5)
    V_t5, U6, V_t6 = Calcular_U6_Vt6(U5_atualizado, V_n5, beta_5, f_e5, mu)

    return {
        "Y": Y.GetValue(),
        "Ns": Ns.GetValue("unitless"),
        "classificacoes": classificacoes,
        "eta_h": eta_h.GetValue("unitless"),
        "eta_a": eta_a.GetValue("unitless"),
        "eta_m": eta_m.GetValue("unitless"),
        "eta_v": eta_v.GetValue("unitless"),
        "eta_t": eta_t.GetValue("unitless"),
        "W_acio_W": W_acio.GetValue("W"),
        "W_acio_kW": W_acio.GetValue("kW"),
        "d_e_cm": d_e.GetValue("cm"),
        "Va": Va.GetValue("m/s"),
        "K_Va": K_Va.GetValue("unitless"),
        "d_c": d_c.GetValue("m"),
        "D_a": D_a.GetValue("m"),
        "Psi": Psi.GetValue("unitless"),
        "U5": U5.GetValue("m/s"),
        "R5": R5.GetValue("m"),
        "beta_5": beta_5.GetValue("dega"),
        "R4": R4.GetValue("m"),
        "V_n3": V_n3.GetValue("m/s"),
        "b4_mm": b4.GetValue("mm"),
        "f_e4": f_e4.GetValue("unitless"),
        "V4": V4.GetValue("m/s"),
        "U4": U4.GetValue("m/s"),
        "beta4": beta4.GetValue("dega"),
        "N_pas": N_pas.GetValue("unitless"),
        "N_pas_adotado": N_pas_adotado.GetValue("unitless"),
        "V_n5": V_n5.GetValue("m/s"),
        "D5": D5.GetValue("m"),
        "f_e5": f_e5.GetValue("unitless"),
        "b5_mm": b5.GetValue("mm"),
        "e_mm": e.GetValue("mm"),
        "D4_mm": D4.GetValue("mm"),
        "t4_mm": t4.GetValue("mm"),
        "e_t4_mm": e_t4.GetValue("mm"),
        "f_e4_calculado": f_e4_calculado.GetValue("unitless"),
        "V4_atualizado": V4_atualizado.GetValue("m/s"),
        "beta4_atualizado": beta4_atualizado.GetValue("dega"),
        "S_f": S_f.GetValue("m2"),
        "K_p": K_p.GetValue("unitless"),
        "mu": mu.GetValue("unitless"),
        "Y_pa": Y_pa.GetValue("J/kg"),
        "a": a.GetValue("unitless"),
        "Y_pa_inf": Y_pa_inf.GetValue("J/kg"),
        "U5_atualizado": U5_atualizado.GetValue("m/s"),
        "R5_atualizado": R5_atualizado.GetValue("m"),
        "D5_atualizado": D5_atualizado.GetValue("m"),
        "b5_atualizado_mm": b5_atualizado.GetValue("mm"),
        "V_t5": V_t5.GetValue("m/s"),
        "U6": U6.GetValue("m/s"),
        "V_t6": V_t6.GetValue("m/s"),
        "relacao_R4_R5": relacao_R4_R5.GetValue(),
    }