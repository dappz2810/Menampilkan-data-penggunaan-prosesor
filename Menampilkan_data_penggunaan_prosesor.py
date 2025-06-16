import psutil
import time
import os
import platform
from datetime import datetime
import threading
import json


class CPUMonitor:
    def __init__(self):
        self.monitoring = False
        self.cpu_history = []
        self.max_history = 60

    def get_cpu_info(self):
        """Mendapatkan informasi dasar CPU"""
        try:
            info = {
                'processor': platform.processor(),
                'architecture': platform.architecture()[0],
                'machine': platform.machine(),
                'cores_physical': psutil.cpu_count(logical=False),
                'cores_logical': psutil.cpu_count(logical=True),
                'max_frequency': f"{psutil.cpu_freq().max:.2f} MHz" if psutil.cpu_freq() else "N/A",
                'current_frequency': f"{psutil.cpu_freq().current:.2f} MHz" if psutil.cpu_freq() else "N/A"
            }
            return info
        except Exception as e:
            return {'error': str(e)}

    def get_cpu_usage(self, interval=1):
        """Mendapatkan penggunaan CPU"""
        try:
            cpu_percent = psutil.cpu_percent(interval=interval)

            cpu_per_core = psutil.cpu_percent(interval=interval, percpu=True)

            try:
                load_avg = os.getloadavg()
            except (OSError, AttributeError):
                load_avg = None

            cpu_times = psutil.cpu_times()

            return {
                'total_usage': cpu_percent,
                'per_core': cpu_per_core,
                'load_average': load_avg,
                'times': {
                    'user': cpu_times.user,
                    'system': cpu_times.system,
                    'idle': cpu_times.idle,
                    'iowait': getattr(cpu_times, 'iowait', 0),
                    'interrupt': getattr(cpu_times, 'interrupt', 0)
                }
            }
        except Exception as e:
            return {'error': str(e)}

    def get_cpu_temperature(self):
        """Mendapatkan suhu CPU (jika tersedia)"""
        try:
            temps = psutil.sensors_temperatures()
            cpu_temps = []

            for name, entries in temps.items():
                if 'cpu' in name.lower() or 'core' in name.lower():
                    for entry in entries:
                        cpu_temps.append({
                            'label': entry.label or f"{name}",
                            'current': entry.current,
                            'high': entry.high,
                            'critical': entry.critical
                        })

            return cpu_temps if cpu_temps else None
        except:
            return None

    def display_cpu_info(self):
        """Menampilkan informasi CPU"""
        print("=" * 70)
        print("                    INFORMASI PROSESOR")
        print("=" * 70)

        cpu_info = self.get_cpu_info()

        if 'error' in cpu_info:
            print(f"Error: {cpu_info['error']}")
            return

        print(f"Prosesor         : {cpu_info['processor']}")
        print(f"Arsitektur       : {cpu_info['architecture']}")
        print(f"Tipe Mesin       : {cpu_info['machine']}")
        print(f"Core Fisik       : {cpu_info['cores_physical']}")
        print(f"Core Logical     : {cpu_info['cores_logical']}")
        print(f"Frekuensi Max    : {cpu_info['max_frequency']}")
        print(f"Frekuensi Saat Ini: {cpu_info['current_frequency']}")
        print("=" * 70)

    def display_cpu_usage(self):
        """Menampilkan penggunaan CPU sekali"""
        print("\nMengambil data penggunaan CPU...")
        usage_data = self.get_cpu_usage()

        if 'error' in usage_data:
            print(f"Error: {usage_data['error']}")
            return

        print("\n" + "=" * 70)
        print("                  PENGGUNAAN PROSESOR")
        print("=" * 70)
        print(f"Waktu            : {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
        print(f"Penggunaan Total : {usage_data['total_usage']:.1f}%")

        self.print_progress_bar(usage_data['total_usage'], "Total CPU")

        print(f"\nPenggunaan Per Core:")
        print("-" * 40)
        for i, core_usage in enumerate(usage_data['per_core']):
            print(f"Core {i + 1:2d}        : {core_usage:5.1f}%", end="  ")
            self.print_mini_bar(core_usage)

        if usage_data['load_average']:
            print(
                f"\nLoad Average     : {usage_data['load_average'][0]:.2f}, {usage_data['load_average'][1]:.2f}, {usage_data['load_average'][2]:.2f}")

        times = usage_data['times']
        print(f"\nWaktu CPU (detik):")
        print(f"  User           : {times['user']:.2f}")
        print(f"  System         : {times['system']:.2f}")
        print(f"  Idle           : {times['idle']:.2f}")
        if times['iowait'] > 0:
            print(f"  IO Wait        : {times['iowait']:.2f}")

        temp_data = self.get_cpu_temperature()
        if temp_data:
            print(f"\nSuhu CPU:")
            for temp in temp_data:
                print(f"  {temp['label']:12s}: {temp['current']:.1f}°C", end="")
                if temp['high']:
                    print(f" (Max: {temp['high']:.1f}°C)", end="")
                print()

        print("=" * 70)

    def print_progress_bar(self, percentage, label="", length=50):
        """Menampilkan progress bar"""
        filled = int(length * percentage / 100)
        bar = "█" * filled + "░" * (length - filled)
        color = self.get_color_by_usage(percentage)
        print(f"{label:15s}: [{bar}] {percentage:5.1f}%")

    def print_mini_bar(self, percentage, length=10):
        """Menampilkan mini progress bar"""
        filled = int(length * percentage / 100)
        bar = "█" * filled + "░" * (length - filled)
        print(f"[{bar}]")

    def get_color_by_usage(self, usage):
        """Mendapatkan warna berdasarkan penggunaan CPU"""
        if usage < 30:
            return "green"
        elif usage < 70:
            return "yellow"
        else:
            return "red"

    def real_time_monitor(self, duration=60, interval=1):
        """Monitor CPU secara real-time"""
        print(f"\n{'=' * 70}")
        print("                 MONITOR REAL-TIME CPU")
        print(f"Duration: {duration} detik | Interval: {interval} detik")
        print("Tekan Ctrl+C untuk berhenti")
        print(f"{'=' * 70}")

        try:
            for i in range(duration):
                os.system('cls' if os.name == 'nt' else 'clear')

                print(f"Monitor CPU Real-time - {i + 1}/{duration} detik")
                print(f"Waktu: {datetime.now().strftime('%H:%M:%S')}")
                print("-" * 70)

                usage_data = self.get_cpu_usage(interval=0.1)

                if 'error' not in usage_data:
                    print(f"CPU Total: {usage_data['total_usage']:5.1f}%", end="  ")
                    self.print_mini_bar(usage_data['total_usage'], 30)

                    print("\nPer Core:")
                    for j, core_usage in enumerate(usage_data['per_core']):
                        if j % 4 == 0 and j > 0:  # New line every 4 cores
                            print()
                        print(f"C{j + 1}:{core_usage:4.1f}%", end="  ")

                    print("\n" + "-" * 70)

                    self.cpu_history.append({
                        'time': datetime.now(),
                        'usage': usage_data['total_usage']
                    })

                    if len(self.cpu_history) > self.max_history:
                        self.cpu_history.pop(0)

                time.sleep(max(0, interval - 0.1))

        except KeyboardInterrupt:
            print("\n\nMonitoring dihentikan oleh user.")
        except Exception as e:
            print(f"\nError during monitoring: {e}")

    def show_cpu_history(self):
        """Menampilkan riwayat penggunaan CPU"""
        if not self.cpu_history:
            print("Tidak ada data riwayat. Jalankan monitoring terlebih dahulu.")
            return

        print("\n" + "=" * 70)
        print("                   RIWAYAT PENGGUNAAN CPU")
        print("=" * 70)

        for i, data in enumerate(self.cpu_history[-20:]):
            time_str = data['time'].strftime('%H:%M:%S')
            usage = data['usage']
            print(f"{time_str} | {usage:5.1f}% ", end="")
            self.print_mini_bar(usage, 20)

        usages = [data['usage'] for data in self.cpu_history]
        print(f"\nStatistik:")
        print(f"  Rata-rata : {sum(usages) / len(usages):5.1f}%")
        print(f"  Minimum   : {min(usages):5.1f}%")
        print(f"  Maksimum  : {max(usages):5.1f}%")
        print("=" * 70)

    def save_cpu_data(self, filename="cpu_data.json"):
        """Menyimpan data CPU ke file"""
        try:
            cpu_info = self.get_cpu_info()
            usage_data = self.get_cpu_usage()

            data = {
                'timestamp': datetime.now().isoformat(),
                'cpu_info': cpu_info,
                'current_usage': usage_data,
                'history': [
                    {
                        'time': entry['time'].isoformat(),
                        'usage': entry['usage']
                    } for entry in self.cpu_history
                ]
            }

            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)

            print(f"Data CPU berhasil disimpan ke {filename}")

        except Exception as e:
            print(f"Error menyimpan data: {e}")


def interactive_menu():
    """Menu interaktif untuk program"""
    monitor = CPUMonitor()

    while True:
        print("INFO PENGGUNAAN PROSESOR")
        print("1. Tampilkan informasi prosesor")
        print("2. Tampilkan penggunaan CPU saat ini")
        print("3. Monitor real-time (60 detik)")
        print("4. Monitor real-time (custom duration)")
        print("5. Tampilkan riwayat penggunaan")
        print("6. Simpan data ke file")
        print("7. Keluar")

        try:
            choice = input("Pilih opsi (1-7): ").strip()

            if choice == '1':
                monitor.display_cpu_info()
            elif choice == '2':
                monitor.display_cpu_usage()
            elif choice == '3':
                monitor.real_time_monitor(60, 1)
            elif choice == '4':
                try:
                    duration = int(input("Masukkan durasi (detik): "))
                    interval = float(input("Masukkan interval (detik, default 1): ") or "1")
                    monitor.real_time_monitor(duration, interval)
                except ValueError:
                    print("Input tidak valid!")
            elif choice == '5':
                monitor.show_cpu_history()
            elif choice == '6':
                filename = input("Nama file (default: cpu_data.json): ").strip()
                if not filename:
                    filename = "cpu_data.json"
                monitor.save_cpu_data(filename)
            elif choice == '7':
                print("\nTerima kasih telah menggunakan CPU Monitor!")
                break
            else:
                print("Pilihan tidak valid. Silakan pilih 1-7.")

        except KeyboardInterrupt:
            print("\n\nProgram dihentikan oleh user.")
            break
        except Exception as e:
            print(f"Terjadi error: {e}")


if __name__ == "__main__":
    print("Starting CPU Monitor Program...")
    print("Note: Pastikan module 'psutil' terinstall (pip install psutil)")

    try:
        interactive_menu()
    except ImportError as e:
        if "psutil" in str(e):
            print("\nError: Module 'psutil' tidak ditemukan.")
            print("Install dengan perintah: pip install psutil")
        else:
            print(f"Error importing modules: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
