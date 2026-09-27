Ein Installer für Windows (.exe) kann sehr leicht mit **Inno Setup** erstellt werden.
1. Lade [Inno Setup](https://jrsoftware.org/isinfo.php) herunter und installiere es.
2. Erstelle ein neues Script mit dem Wizard.
3. Wähle die in `dist/Chronix` oder als `dist/Chronix.exe` kompilierte Datei aus.
4. (Optional) Um .worldcal Dateien automatisch mit Chronix zu verknüpfen, füge diese Zeilen am Ende des Inno Setup Scripts (vor dem Kompilieren) unter `[Registry]` ein:

```inno
[Registry]
Root: HKCR; Subkey: ".worldcal"; ValueType: string; ValueName: ""; ValueData: "ChronixProject"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "ChronixProject"; ValueType: string; ValueName: ""; ValueData: "Chronix World Calendar"; Flags: uninsdeletekey
Root: HKCR; Subkey: "ChronixProject\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\Chronix.exe,0"
Root: HKCR; Subkey: "ChronixProject\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\Chronix.exe"" ""%1"""
```
Das sorgt dafür, dass ein Doppelklick auf eine `.worldcal` Datei das Programm direkt öffnet!
