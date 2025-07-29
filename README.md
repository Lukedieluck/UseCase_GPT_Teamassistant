
Projektzusammenfassung – Scrum GPT Team-Assistant


Du entwickelst ein Python-basiertes Tool, das folgende Ziele verfolgt:

Teammitglieder können ihre aktuellen Stimmungen/Feelings anonymisiert über das Tool erfassen und in einer Vektor-Datenbank speichern.

Bei einer späteren Abfrage wie „Wie ist die Stimmung im Team?“ greift das Tool auf diese Einträge in der Vector-DB zu und kann daraus aggregierte oder kontextbezogene Rückmeldungen erzeugen. Diese Ausgabe muss Datenschutzkonform erfolgen und auf vertraulicher Basis erfolgen.

Die OpenAI GPT-API wird genutzt, um Antworten im Scrum-Kontext bereitzustellen (z. B. zur Moderation, zum Umgang mit Konflikten oder zur allgemeinen Beratung). Dies erfolgt Projektspezifisch und je nach individuellen Kontext der Teammitglieder.

Die System Prompts und RAG-Einträge gibt dabei weiterhin den Berater-Kontext und klare Antwortregeln vor.

Der User Prompt kann nun sowohl „klassische“ Scrum-Fragen als auch Fragen zur Teamstimmung enthalten.

Die Projektstruktur bleibt klar: Python-Skript(e), requirements.txt, README.md, Vector-DB-Anbindung.

Kernidee:
Ein AI-gestütztes Beratungstool, das die Teamstimmung anonym sammelt und mithilfe einer Vector-DB sowie GPT-Modell auswertbar und abrufbar macht – z. B. als Antwort auf „Wie ist die Stimmung im Team?“
