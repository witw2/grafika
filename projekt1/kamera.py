import pygame
import math
import sys

SZEROKOSC_EKRANU, WYSOKOSC_EKRANU = 800, 600
BIALY = (255, 255, 255)
KOLOR_CZERWONY = (200, 0, 0)
KOLOR_ZIELONY = (0, 180, 0)
KOLOR_NIEBIESKI = (0, 0, 200)
KOLOR_MAGENTA = (200, 0, 200)
KOLOR_CYJAN = (0, 180, 180)


mnoznik=2
PREDKOSC_RUCHU = 5.0/mnoznik
PREDKOSC_OBROTU = 0.01/mnoznik
PREDKOSC_ZOOM = 0.01/mnoznik
BLISKIE_CIECIE = 1.0/mnoznik

POCZATKOWY_KAM_X, POCZATKOWY_KAM_Y, POCZATKOWY_KAM_Z = 0.0, 50.0, -100.0
POCZATKOWE_ODCHYLENIE, POCZATKOWE_POCHYLENIE, POCZATKOWE_PRZECHYLENIE = 0.0, 0.0, 0.0
POCZATKOWE_POLE_WIDZENIA = 60 * math.pi / 180

kam_x, kam_y, kam_z = POCZATKOWY_KAM_X, POCZATKOWY_KAM_Y, POCZATKOWY_KAM_Z
odchylenie, pochylenie, przechylenie = POCZATKOWE_ODCHYLENIE, POCZATKOWE_POCHYLENIE, POCZATKOWE_PRZECHYLENIE
pole_widzenia = POCZATKOWE_POLE_WIDZENIA
MIN_POLE_WIDZENIA = 20 * math.pi / 180
MAX_POLE_WIDZENIA = 120 * math.pi / 180

def stworz_wierzcholki_prostopadloscianu(sx, sy, sz, szerokosc, wysokosc, glebokosc):
    pol_szer, pol_wys, pol_gleb = szerokosc / 2, wysokosc / 2, glebokosc / 2
    return [
        {'x': sx - pol_szer, 'y': sy - pol_wys, 'z': sz - pol_gleb}, {'x': sx + pol_szer, 'y': sy - pol_wys, 'z': sz - pol_gleb},
        {'x': sx + pol_szer, 'y': sy + pol_wys, 'z': sz - pol_gleb}, {'x': sx - pol_szer, 'y': sy + pol_wys, 'z': sz - pol_gleb},
        {'x': sx - pol_szer, 'y': sy - pol_wys, 'z': sz + pol_gleb}, {'x': sx + pol_szer, 'y': sy - pol_wys, 'z': sz + pol_gleb},
        {'x': sx + pol_szer, 'y': sy + pol_wys, 'z': sz + pol_gleb}, {'x': sx - pol_szer, 'y': sy + pol_wys, 'z': sz + pol_gleb}
    ]

krawedzie_prostopadloscianu = [
    (0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6),
    (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)
]

dane_sceny = [
    {'wierzcholki': stworz_wierzcholki_prostopadloscianu(sx=0, sy=0, sz=600, szerokosc=150, wysokosc=150, glebokosc=150), 'krawedzie': krawedzie_prostopadloscianu, 'kolor': KOLOR_CZERWONY },
    {'wierzcholki': stworz_wierzcholki_prostopadloscianu(sx=-250, sy=100, sz=800, szerokosc=50, wysokosc=300, glebokosc=50), 'krawedzie': krawedzie_prostopadloscianu, 'kolor': KOLOR_ZIELONY },
    {'wierzcholki': stworz_wierzcholki_prostopadloscianu(sx=250, sy=-50, sz=1000, szerokosc=300, wysokosc=50, glebokosc=200), 'krawedzie': krawedzie_prostopadloscianu, 'kolor': KOLOR_NIEBIESKI },
    {'wierzcholki': stworz_wierzcholki_prostopadloscianu(sx=0, sy=0, sz=1300, szerokosc=400, wysokosc=50, glebokosc=50), 'krawedzie': krawedzie_prostopadloscianu, 'kolor': KOLOR_MAGENTA },
    {'wierzcholki': stworz_wierzcholki_prostopadloscianu(sx=150, sy=150, sz=700, szerokosc=80, wysokosc=80, glebokosc=250), 'krawedzie': krawedzie_prostopadloscianu, 'kolor': KOLOR_CYJAN }
]

def pobierz_baze_kamery(biezace_odchylenie, biezace_pochylenie, biezace_przechylenie):
    cos_y, sin_y = math.cos(biezace_odchylenie), math.sin(biezace_odchylenie)
    cos_p, sin_p = math.cos(biezace_pochylenie), math.sin(biezace_pochylenie)
    cos_r, sin_r = math.cos(biezace_przechylenie), math.sin(biezace_przechylenie)
    do_przodu = { 'x': sin_y * cos_p, 'y': -sin_p, 'z': cos_y * cos_p }
    prawo0 = { 'x': cos_y, 'y': 0, 'z': -sin_y }
    gora0 = {
        'x': do_przodu['y'] * prawo0['z'] - do_przodu['z'] * prawo0['y'],
        'y': do_przodu['z'] * prawo0['x'] - do_przodu['x'] * prawo0['z'],
        'z': do_przodu['x'] * prawo0['y'] - do_przodu['y'] * prawo0['x']
    }
    prawo = {
        'x': prawo0['x'] * cos_r - gora0['x'] * sin_r,
        'y': prawo0['y'] * cos_r - gora0['y'] * sin_r,
        'z': prawo0['z'] * cos_r - gora0['z'] * sin_r
    }
    gora = {
        'x': prawo0['x'] * sin_r + gora0['x'] * cos_r,
        'y': prawo0['y'] * sin_r + gora0['y'] * cos_r,
        'z': prawo0['z'] * sin_r + gora0['z'] * cos_r
    }
    return do_przodu, prawo, gora

def swiat_do_kamery(wierzcholek, baza_p, baza_pr, baza_g):
    vx = wierzcholek['x'] - kam_x
    vy = wierzcholek['y'] - kam_y
    vz = wierzcholek['z'] - kam_z
    return {
        'x': vx * baza_pr['x'] + vy * baza_pr['y'] + vz * baza_pr['z'],
        'y': vx * baza_g['x'] + vy * baza_g['y'] + vz * baza_g['z'],
        'z': vx * baza_p['x'] + vy * baza_p['y'] + vz * baza_p['z']
    }

def rzutuj_wierzcholek(w):
    tg_pol_widzenia = math.tan(pole_widzenia / 2)
    if w['z'] < BLISKIE_CIECIE or tg_pol_widzenia <= 0:
        return None
    d = (WYSOKOSC_EKRANU / 2) / tg_pol_widzenia
    ekran_x = (w['x'] * d) / w['z'] + SZEROKOSC_EKRANU / 2
    ekran_y = -(w['y'] * d) / w['z'] + WYSOKOSC_EKRANU / 2
    return int(ekran_x), int(ekran_y)

pygame.init()
ekran = pygame.display.set_mode((SZEROKOSC_EKRANU, WYSOKOSC_EKRANU))
pygame.display.set_caption("Kamera wirtualna")
zegar = pygame.time.Clock()

dziala = True
while dziala:
    for zdarzenie in pygame.event.get():
        if zdarzenie.type == pygame.QUIT:
            dziala = False
        if zdarzenie.type == pygame.KEYDOWN:
             if zdarzenie.key == pygame.K_ESCAPE:
                 dziala = False
             if zdarzenie.key == pygame.K_r:
                 kam_x, kam_y, kam_z = POCZATKOWY_KAM_X, POCZATKOWY_KAM_Y, POCZATKOWY_KAM_Z
                 odchylenie, pochylenie, przechylenie = POCZATKOWE_ODCHYLENIE, POCZATKOWE_POCHYLENIE, POCZATKOWE_PRZECHYLENIE
                 pole_widzenia = POCZATKOWE_POLE_WIDZENIA

    klawisze = pygame.key.get_pressed()
    do_przodu, prawo, gora = pobierz_baze_kamery(odchylenie, pochylenie, przechylenie)

    delta_x, delta_y, delta_z = 0.0, 0.0, 0.0
    biezaca_predkosc_ruchu = PREDKOSC_RUCHU * 3 if klawisze[pygame.K_LSHIFT] else PREDKOSC_RUCHU
    if klawisze[pygame.K_w]:
        delta_x += do_przodu['x'] * biezaca_predkosc_ruchu
        delta_y += do_przodu['y'] * biezaca_predkosc_ruchu
        delta_z += do_przodu['z'] * biezaca_predkosc_ruchu
    if klawisze[pygame.K_s]:
        delta_x -= do_przodu['x'] * biezaca_predkosc_ruchu
        delta_y -= do_przodu['y'] * biezaca_predkosc_ruchu
        delta_z -= do_przodu['z'] * biezaca_predkosc_ruchu
    if klawisze[pygame.K_a]:
        delta_x -= prawo['x'] * biezaca_predkosc_ruchu
        delta_z -= prawo['z'] * biezaca_predkosc_ruchu
    if klawisze[pygame.K_d]:
        delta_x += prawo['x'] * biezaca_predkosc_ruchu
        delta_z += prawo['z'] * biezaca_predkosc_ruchu
    if klawisze[pygame.K_SPACE]:
        delta_y += biezaca_predkosc_ruchu
    if klawisze[pygame.K_f] or klawisze[pygame.K_LCTRL]:
        delta_y -= biezaca_predkosc_ruchu

    kam_x += delta_x
    kam_y += delta_y
    kam_z += delta_z

    delta_odchylenie, delta_pochylenie, delta_przechylenie = 0.0, 0.0, 0.0
    if klawisze[pygame.K_LEFT]: delta_odchylenie -= PREDKOSC_OBROTU
    if klawisze[pygame.K_RIGHT]: delta_odchylenie += PREDKOSC_OBROTU
    if klawisze[pygame.K_UP]: delta_pochylenie -= PREDKOSC_OBROTU
    if klawisze[pygame.K_DOWN]: delta_pochylenie += PREDKOSC_OBROTU
    if klawisze[pygame.K_q]: delta_przechylenie -= PREDKOSC_OBROTU
    if klawisze[pygame.K_e]: delta_przechylenie += PREDKOSC_OBROTU

    odchylenie += delta_odchylenie
    pochylenie += delta_pochylenie
    przechylenie += delta_przechylenie
    max_pochylenie = math.pi / 2 - 0.01
    pochylenie = max(min(pochylenie, max_pochylenie), -max_pochylenie)

    if klawisze[pygame.K_EQUALS] or klawisze[pygame.K_PLUS] or klawisze[pygame.K_KP_PLUS]:
        pole_widzenia -= PREDKOSC_ZOOM
    if klawisze[pygame.K_MINUS] or klawisze[pygame.K_KP_MINUS]:
        pole_widzenia += PREDKOSC_ZOOM
    pole_widzenia = max(min(pole_widzenia, MAX_POLE_WIDZENIA), MIN_POLE_WIDZENIA)

    ekran.fill(BIALY)

    for dane_ksztaltu in dane_sceny:
        wierzcholki = dane_ksztaltu['wierzcholki']
        krawedzie = dane_ksztaltu['krawedzie']
        kolor = dane_ksztaltu['kolor']
        rzutowane_punkty = []
        for wierzcholek in wierzcholki:
            wierzcholek_kamery = swiat_do_kamery(wierzcholek, do_przodu, prawo, gora)
            rzutowany = rzutuj_wierzcholek(wierzcholek_kamery)
            rzutowane_punkty.append(rzutowany)
        for krawedz in krawedzie:
            indeks_p1, indeks_p2 = krawedz
            p1 = rzutowane_punkty[indeks_p1]
            p2 = rzutowane_punkty[indeks_p2]
            if p1 is not None and p2 is not None:
                pygame.draw.line(ekran, kolor, p1, p2, 2)

    pygame.display.flip()
    zegar.tick(60*mnoznik)

pygame.quit()
sys.exit()