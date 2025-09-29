<h1>🧠 Caldras</h1>
<p>Caldras nasce da un’esigenza personale: annotare pensieri, idee e appunti in modo sicuro, senza rinunciare alla semplicità.<br>
È un piccolo strumento scritto in Python, pensato per chi ama lavorare da terminale ma non disdegna una GUI minimalista.</p>
<p>Durante lo sviluppo, ho avuto il piacere di collaborare con un assistente AI che ha contribuito con suggerimenti, ottimizzazioni e un pizzico di creatività. Il risultato è un'applicazione leggera, funzionale e multipiattaforma.</p>

<h2>📦 Versioni disponibili</h2>
<ul>
  <li><code>caldras</code> — versione <strong>terminal-based</strong> per Linux</li>
  <li><code>caldras-gui</code> — versione <strong>console-style GUI</strong> per Linux</li>
  <li><code>wcaldras.py</code> — versione <strong>terminal-based</strong> per Windows</li>
  <li><code>wcaldras_gui.py</code> — versione <strong>console-style GUI</strong> per Windows</li>
</ul>
<p>Tutte le versioni condividono lo stesso file dati: <strong><a href="https://note.dat">note.dat</a></strong></p>

<h2>🚀 Installazione</h2>
<h3>Linux</h3>
<pre><code>chmod +x caldras caldras-gui
sudo mv caldras caldras-gui /usr/local/bin/
</code></pre>
<p>Facoltativo: crea un file <code>.desktop</code> per avviare <code>caldras-gui</code> senza console.</p>

<h3>Windows</h3>
<pre><code>pip install -U pyinstaller
pyinstaller --noconfirm --onefile --windowed --icon=icon_caldras.png wcaldras-gui.py
</code></pre>

<h2>📚 Dipendenze</h2>
<h3>Linux</h3>
<pre><code>pip install cryptography markdown weasyprint rich
</code></pre>
<p>oppure su EndeavourOS:</p>
<pre><code>yay -S python-markdown python-markdown2 python-weasyprint python-cryptography tk python-rich
</code></pre>

<h3>Windows</h3>
<pre><code>pip install cryptography markdown colorama rich
</code></pre>
<p>Inoltre, installa <a href="https://wkhtmltopdf.org/downloads.html">wkhtmltopdf</a> e aggiungilo al PATH di sistema.</p>

<h2>⚠️ Note importanti</h2>
<ul>
  <li>Il file <a href="https://note.dat">note.dat</a> verrà creato nella directory corrente della shell.</li>
  <li>Il software è stato realizzato per uso personale, con il supporto creativo e tecnico di un assistente AI.</li>
</ul>
