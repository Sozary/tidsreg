#!/usr/bin/env python3
"""
Script de debug pour analyser le parsing HTML de Tidsreg.
Sauvegarde le HTML et les données parsées pour analyse.

Usage:
    python3 debug_parser.py <username> <password> [date]
    ou
    python3 debug_parser.py  (pour mode interactif)
"""

import json
import sys
from datetime import datetime
from tidsreg_client import TidsregClient
from getpass import getpass

def main():
    print("🔍 Script de debug Tidsreg Parser")
    print("=" * 50)

    # Get credentials from args or prompt
    if len(sys.argv) >= 3:
        username = sys.argv[1]
        password = sys.argv[2]
        date = sys.argv[3] if len(sys.argv) >= 4 else "2025-10-01"
        print(f"📝 Mode arguments: username={username}, date={date}")
    else:
        username = input("Username Tidsreg: ")
        password = getpass("Password Tidsreg: ")
        date_input = input("Date à analyser (YYYY-MM-DD) [défaut: 2025-10-01]: ").strip()
        date = date_input if date_input else "2025-10-01"

    print(f"\n📅 Analyse de la date: {date}")
    print("=" * 50)

    # Create client and login
    client = TidsregClient()
    print("\n🔐 Connexion à Tidsreg...")
    login_result = client.login(username, password)

    if "error" in login_result:
        print(f"❌ Erreur de connexion: {login_result['error']}")
        return

    print("✅ Connecté!")

    # Get registered hours
    print(f"\n📊 Récupération des heures pour {date}...")
    result = client.get_registered_hours(date)

    if "error" in result:
        print(f"❌ Erreur: {result['error']}")
        return

    # Save HTML
    hours_date = client._convert_date_to_hours_format(date)
    url = f"{client.BASE_URL}/Hours/{hours_date}"
    response = client.session.get(url, allow_redirects=True)

    html_filename = f"debug_html_{date.replace('-', '')}.html"
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(response.text)
    print(f"💾 HTML sauvegardé: {html_filename}")

    # Save parsed data
    json_filename = f"debug_parsed_{date.replace('-', '')}.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"💾 Données parsées sauvegardées: {json_filename}")

    # Display summary
    print("\n" + "=" * 50)
    print("📋 RÉSUMÉ DES DONNÉES PARSÉES")
    print("=" * 50)

    print(f"\n✅ Status: {result.get('ok', False)}")
    print(f"📅 Date: {result.get('date')}")
    print(f"📊 Semaine: {result.get('week_info', {}).get('week')} de {result.get('week_info', {}).get('year')}")
    print(f"📏 Taille HTML: {result.get('raw_html_size', 0):,} bytes")

    registrations = result.get('registrations', [])
    print(f"\n📝 Nombre d'entrées parsées: {len(registrations)}")

    if registrations:
        print("\n🔍 Aperçu des entrées (10 premières):")
        for i, reg in enumerate(registrations[:10], 1):
            print(f"\n  {i}. Level: {reg.get('level', 'N/A')}")
            if 'data' in reg:
                print(f"     Data: {reg['data']}")
            if 'hours' in reg and reg['hours']:
                print(f"     Hours: {reg['hours']}")
            if 'value' in reg and reg['value']:
                print(f"     Value: {reg['value']}")

    totals = result.get('totals', {})
    if totals:
        print(f"\n📊 Totaux trouvés: {len(totals)}")
        print("   Exemples:")
        for key, value in list(totals.items())[:5]:
            print(f"     {key}: {value}")

    print("\n" + "=" * 50)
    print("✅ Debug terminé!")
    print(f"📁 Fichiers créés:")
    print(f"   - {html_filename}")
    print(f"   - {json_filename}")
    print("\n💡 Partage ces fichiers pour analyse approfondie")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
