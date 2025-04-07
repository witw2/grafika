import pygame
import sys

# Inicjalizacja Pygame
pygame.init()

# Inicjalizacja modułu joysticka
pygame.joystick.init()

# --- Konfiguracja Okna (minimalne, do obsługi zdarzeń) ---
SZEROKOSC_OKNA, WYSOKOSC_OKNA = 450, 200  # Trochę szersze okno
ekran = pygame.display.set_mode((SZEROKOSC_OKNA, WYSOKOSC_OKNA))
pygame.display.set_caption("Test Akcji Kontrolera")
zegar = pygame.time.Clock()
bialy = (255, 255, 255)
czarny = (0, 0, 0)
font = pygame.font.Font(None, 24)

# --- Wykrywanie Kontrolera ---
joystick = None
nazwa_kontrolera = "Brak"
liczba_przyciskow = 0
liczba_osi = 0
liczba_hatow = 0
liczba_joystickow = pygame.joystick.get_count()

if liczba_joystickow > 0:
    try:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        nazwa_kontrolera = joystick.get_name()
        liczba_przyciskow = joystick.get_numbuttons()
        liczba_osi = joystick.get_numaxes()
        liczba_hatow = joystick.get_numhats()
        print(f"Znaleziono kontroler: {nazwa_kontrolera}")
        print(f"Liczba przycisków: {liczba_przyciskow}")
        print(f"Liczba osi: {liczba_osi}")
        print(f"Liczba hatów (D-padów): {liczba_hatow}")
        print("\nWykonuj akcje na kontrolerze (przyciski, analogi, D-pad)...")
    except pygame.error as e:
        print(f"Błąd inicjalizacji joysticka: {e}")
        joystick = None
else:
    print("Nie znaleziono żadnego kontrolera.")
    print("Podłącz kontroler i uruchom program ponownie.")

# --- Przechowywanie ostatniego stanu dla wyświetlania ---
ostatnia_akcja_typ = ""
ostatnia_akcja_wartosc = ""

# --- Główna Pętla ---
dziala = True
while dziala:
    # --- Obsługa Zdarzeń ---
    for zdarzenie in pygame.event.get():
        if zdarzenie.type == pygame.QUIT:
            dziala = False

        # Sprawdzamy, czy zdarzenie pochodzi od naszego kontrolera (jeśli istnieje)
        if joystick is None or getattr(zdarzenie, 'instance_id', -1) != joystick.get_instance_id():
            if zdarzenie.type >= pygame.JOYAXISMOTION and zdarzenie.type <= pygame.JOYBUTTONUP:  # Ignoruj zdarzenia joysticka, jeśli nie mamy joysticka
                continue

        # --- Zdarzenia Kontrolera ---
        if zdarzenie.type == pygame.JOYBUTTONDOWN:
            print(f"Przycisk WCIŚNIĘTY: Indeks={zdarzenie.button}")
            ostatnia_akcja_typ = "Przycisk WCIŚNIĘTY"
            ostatnia_akcja_wartosc = f"Indeks={zdarzenie.button}"

        elif zdarzenie.type == pygame.JOYBUTTONUP:
            print(f"Przycisk ZWOLNIONY: Indeks={zdarzenie.button}")
            ostatnia_akcja_typ = "Przycisk ZWOLNIONY"
            ostatnia_akcja_wartosc = f"Indeks={zdarzenie.button}"

        elif zdarzenie.type == pygame.JOYAXISMOTION:
            # Osie analogowe generują dużo zdarzeń, wartość jest najważniejsza
            # Można dodać warunek, aby nie drukować dla małych zmian blisko zera
            # if abs(zdarzenie.value) > 0.05:
            print(f"Oś ZMIENIONA: Indeks={zdarzenie.axis}, Wartość={zdarzenie.value:.3f}")
            ostatnia_akcja_typ = "Oś ZMIENIONA"
            ostatnia_akcja_wartosc = f"Indeks={zdarzenie.axis}, Wartość={zdarzenie.value:.3f}"

        elif zdarzenie.type == pygame.JOYHATMOTION:
            print(f"Hat (D-pad) ZMIENIONY: Indeks={zdarzenie.hat}, Wartość={zdarzenie.value}")
            ostatnia_akcja_typ = "Hat (D-pad) ZMIENIONY"
            ostatnia_akcja_wartosc = f"Indeks={zdarzenie.hat}, Wartość={zdarzenie.value}"

        # Można też dodać obsługę JOYBALLMOTION, jeśli kontroler ma trackball

    # --- Rysowanie informacji w oknie ---
    ekran.fill(bialy)
    if joystick is None:
        napis = font.render("Brak kontrolera", True, czarny)
        ekran.blit(napis, (10, 10))
    else:
        napis1 = font.render(f"Kontroler: {nazwa_kontrolera}", True, czarny)
        ekran.blit(napis1, (10, 10))
        napis2 = font.render(f"Przyciski: {liczba_przyciskow}, Osie: {liczba_osi}, Haty: {liczba_hatow}", True, czarny)
        ekran.blit(napis2, (10, 40))

        napis_akcja1 = font.render(f"Ostatnia akcja: {ostatnia_akcja_typ}", True, czarny)
        ekran.blit(napis_akcja1, (10, 70))
        napis_akcja2 = font.render(f"  {ostatnia_akcja_wartosc}", True, czarny)
        ekran.blit(napis_akcja2, (10, 95))

        napis_konsola = font.render("Szczegóły w konsoli!", True, czarny)
        ekran.blit(napis_konsola, (10, 140))

    pygame.display.flip()
    zegar.tick(30)  # Ograniczamy CPU

# --- Zakończenie ---
pygame.quit()
sys.exit()