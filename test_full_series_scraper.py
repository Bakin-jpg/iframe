# test_full_series_scraper.py

from playwright.sync_api import sync_playwright, TimeoutError
import json

def scrape_all_episodes_from_show(show_url):
    """
    (FIXED V4) Mengunjungi halaman detail, klik "Watch Now", menunggu
    daftar episode muncul (tanpa 'networkidle'), lalu scrape semua iframe.
    """
    print("="*50)
    print("   MEMULAI PENGUJIAN SCRAPER UNTUK SEMUA EPISODE (V4 - FIXED)   ")
    print("="*50)
    print(f"URL Halaman Anime: {show_url}\n")
    
    episodes_data = []

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # 1. Buka halaman detail anime
            print(f"1. Menavigasi ke halaman detail anime...")
            page.goto(show_url, timeout=90000, wait_until="domcontentloaded")
            print("   Halaman detail berhasil dimuat.")

            # 2. Cari dan klik tombol "Watch Now"
            watch_now_selector = "a.pulse-button:has-text('Watch Now')"
            print(f"2. Mencari tombol 'Watch Now'...")
            page.wait_for_selector(watch_now_selector, timeout=60000)
            print("   Tombol 'Watch Now' ditemukan. Mengklik tombol...")
            page.locator(watch_now_selector).click()

            # 3. Hapus 'wait_for_load_state'. Langsung tunggu elemen yang kita butuhkan.
            episode_item_selector = "div.episode-item"
            print(f"3. Menunggu daftar episode (konten JS) muncul...")
            page.wait_for_selector(episode_item_selector, timeout=60000)
            
            episode_locators = page.locator(episode_item_selector)
            episode_count = episode_locators.count()
            print(f"   Ditemukan {episode_count} episode di halaman ini.")
            
            # 4. Looping untuk setiap episode
            for i in range(episode_count):
                print(f"\n--- Memproses Episode {i + 1} dari {episode_count} ---")
                
                # Selalu cari ulang elemen di setiap iterasi untuk menghindari error "stale"
                all_episodes = page.locator(episode_item_selector)
                current_episode_element = all_episodes.nth(i)

                episode_number_text = current_episode_element.locator("span.v-chip__content").inner_text()
                print(f"   Nomor Episode: {episode_number_text}")

                # Periksa apakah ini episode yang sedang diputar
                is_playing = current_episode_element.locator("div.v-overlay__content:has-text('Playing')").is_visible()
                
                if not is_playing:
                    print("   Mengklik link episode...")
                    current_episode_element.click()
                    # Tunggu hingga iframe di-reload. Menunggu URL berubah adalah cara yang baik.
                    page.wait_for_function("document.querySelector('div.player-container iframe') !== null", timeout=60000)
                else:
                    print("   Ini adalah episode yang sedang diputar, tidak perlu diklik.")
                
                episode_url = page.url
                print(f"   URL Halaman Episode: {episode_url}")
                
                iframe_src = None
                try:
                    iframe_selector = "div.player-container iframe.player"
                    iframe_element = page.locator(iframe_selector)
                    # Tunggu elemennya visible sebelum ambil atribut
                    iframe_element.wait_for(state="visible", timeout=30000)
                    iframe_src = iframe_element.get_attribute('src')
                    print(f"   Iframe ditemukan: {iframe_src}")
                except TimeoutError:
                    print("   [PERINGATAN] Iframe tidak ditemukan untuk episode ini.")
                    iframe_src = "Not Found"

                episodes_data.append({
                    "episode_number": episode_number_text,
                    "episode_url": episode_url,
                    "iframe_url": iframe_src
                })
                
                # Kita tidak perlu `go_back` karena ini adalah SPA.
                # Klik pada daftar episode hanya mengubah URL dan memuat ulang player,
                # tapi daftar episodenya tetap ada di halaman.

            print("\n" + "="*50)
            print("Semua episode telah diproses.")
            browser.close()

        except Exception as e:
            print(f"\n[ERROR] Terjadi kesalahan fatal: {e}")
            if 'browser' in locals() and browser.is_connected():
                browser.close()
            raise SystemExit(f"Test Gagal: {e}")
            
    return episodes_data

if __name__ == "__main__":
    test_show_url = "https://kickass-anime.ru/potion-wagami-wo-tasukeru-f0c8"
    
    final_data = scrape_all_episodes_from_show(test_show_url)

    if final_data:
        output_filename = "episode_iframes.json"
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)
        
        print(f"\nSTATUS: BERHASIL ✅")
        print(f"Total {len(final_data)} episode diproses dan disimpan di '{output_filename}'")
    else:
        print("\nSTATUS: GAGAL ❌")
        print("Tidak ada data episode yang berhasil diambil.")
