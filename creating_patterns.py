import os
import json
import random
import math
import io
import base64
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import imageio.v2 as imageio  # Use v2 to avoid deprecation warnings

from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)

# --- Collatz Cache Setup ---
CACHE_FILENAME = "collatz_cache.json"
if os.path.exists(CACHE_FILENAME):
    with open(CACHE_FILENAME, "r") as f:
        collatz_cache = json.load(f)
else:
    collatz_cache = {}

def get_cached_collatz(n):
    key = str(n)
    if key in collatz_cache:
        return collatz_cache[key]
    seq = collatz(n)
    collatz_cache[key] = seq
    with open(CACHE_FILENAME, "w") as f:
        json.dump(collatz_cache, f)
    return seq

# --- Series Generation Functions ---
def fibonacci(n):
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    series = [0, 1]
    while len(series) < n:
        series.append(series[-1] + series[-2])
    return series

def collatz(start):
    if start < 1:
        start = 1
    sequence = [start]
    while start != 1:
        if start % 2 == 0:
            start //= 2
        else:
            start = 3 * start + 1
        sequence.append(start)
    return sequence

def is_prime(num):
    if num < 2:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True

def primes(n):
    if n <= 0:
        return []
    prime_list = []
    candidate = 2
    while len(prime_list) < n:
        if is_prime(candidate):
            prime_list.append(candidate)
        candidate += 1
    return prime_list

def triangular_numbers(n):
    return [i * (i + 1) // 2 for i in range(1, n + 1)]

def squares(n):
    return [i ** 2 for i in range(1, n + 1)]

def cubes(n):
    return [i ** 3 for i in range(1, n + 1)]

def factorials(n):
    result = []
    fact = 1
    for i in range(1, n + 1):
        fact *= i
        result.append(fact)
    return result

def powers_of_two(n):
    return [2 ** i for i in range(n)]

def pentagonal_numbers(n):
    return [(3 * i ** 2 - i) // 2 for i in range(1, n + 1)]

def integers(n):
    return list(range(1, n+1))

def generate_series(series_type, n):
    series_type = series_type.lower()
    if series_type == "fibonacci":
        return fibonacci(n)
    elif series_type == "primes":
        return primes(n)
    elif series_type == "triangular":
        return triangular_numbers(n)
    elif series_type == "squares":
        return squares(n)
    elif series_type == "cubes":
        return cubes(n)
    elif series_type == "factorials":
        return factorials(n)
    elif series_type == "powers_of_two":
        return powers_of_two(n)
    elif series_type == "pentagonal":
        return pentagonal_numbers(n)
    elif series_type == "integers":
        return integers(n)
    else:
        raise ValueError("Unknown series type.")

# --- Cumulative Turtle Animation Function ---
def generate_combined_turtle_animation(main_series, left_angle, right_angle, step_length=10, 
                                         stroke_width=3, dpi=100, custom_transform=False, 
                                         left_mod=180, right_mod=180, cmap_name="viridis", 
                                         dark_background=False, consecutive_increment=False,
                                         variable_step=False, rotation_drift=0.0,
                                         symmetry_mirror="None", random_color_variation=False):
    """
    For each number in main_series, use the cached Collatz sequence and simulate a turtle drawing.
    Options:
      - custom_transform: if enabled, turning angle = (number mod mod_value) for each parity.
      - consecutive_increment: extra degree for consecutive same-parity steps.
      - variable_step: step length increases with each step.
      - rotation_drift: constant drift added each step.
      - symmetry_mirror: "None", "Horizontal", or "Vertical" mirror of the drawing.
      - random_color_variation: random color per sequence.
      - dark_background: use dark background.
    Output figure size is 12x12 inches.
    Returns a list of frames for the GIF.
    """
    frames = []
    completed_paths = []
    cmap = plt.get_cmap(cmap_name)
    fig, ax = plt.subplots(figsize=(15, 15), dpi=dpi)
    bg_color = "#222222" if dark_background else "#f0f8ff"
    ax.set_facecolor(bg_color)
    
    for idx, num in enumerate(main_series):
        collatz_start = num if num >= 1 else 1
        seq = get_cached_collatz(collatz_start)
        x_coords = [0]
        y_coords = [0]
        angle = 0
        if random_color_variation:
            current_color = (random.random(), random.random(), random.random())
        else:
            current_color = cmap(idx / max(len(main_series)-1, 1))
        consecutive_odd = 0
        consecutive_even = 0
        
        for i, step in enumerate(seq):
            if custom_transform:
                effective_turn = (step % left_mod) if (step % 2 != 0) else (step % right_mod)
            else:
                if consecutive_increment:
                    if step % 2 != 0:
                        consecutive_odd += 1
                        consecutive_even = 0
                        effective_turn = left_angle + (consecutive_odd - 1)
                    else:
                        consecutive_even += 1
                        consecutive_odd = 0
                        effective_turn = right_angle + (consecutive_even - 1)
                else:
                    effective_turn = left_angle if (step % 2 != 0) else right_angle
            current_step_length = step_length * (1 + 0.05 * i) if variable_step else step_length
            if step % 2 != 0:
                angle += effective_turn
            else:
                angle -= effective_turn
            angle += rotation_drift
            rad = math.radians(angle)
            new_x = x_coords[-1] + current_step_length * math.cos(rad)
            new_y = y_coords[-1] + current_step_length * math.sin(rad)
            x_coords.append(new_x)
            y_coords.append(new_y)
            
            ax.clear()
            ax.set_facecolor(bg_color)
            ax.axis('off')
            for path in completed_paths:
                ax.plot(path['x'], path['y'], color=path['color'], lw=2, alpha=0.6)
            ax.plot(x_coords, y_coords, color=current_color, lw=stroke_width, alpha=0.9)
            if symmetry_mirror == "Horizontal":
                mirrored_x = [-x for x in x_coords]
                ax.plot(mirrored_x, y_coords, color=current_color, lw=stroke_width, alpha=0.9)
            elif symmetry_mirror == "Vertical":
                mirrored_y = [-y for y in y_coords]
                ax.plot(x_coords, mirrored_y, color=current_color, lw=stroke_width, alpha=0.9)
            margin = current_step_length * 2
            all_x = [pt for path in completed_paths for pt in path['x']] + x_coords
            all_y = [pt for path in completed_paths for pt in path['y']] + y_coords
            if all_x and all_y:
                ax.set_xlim(min(all_x)-margin, max(all_x)+margin)
                ax.set_ylim(min(all_y)-margin, max(all_y)+margin)
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            frame = imageio.imread(buf)
            frames.append(frame)
        
        completed_paths.append({'x': x_coords, 'y': y_coords, 'color': current_color})
        for _ in range(5):
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            frame = imageio.imread(buf)
            frames.append(frame)
    plt.close(fig)
    return frames

# --- HTML Template ---
# Removed the "Collatz Input Value" field. A new "Summary" section is added next to the animation.
template = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Artful Collatz Animation</title>
  <style>
    body { font-family: Arial, sans-serif; background: #ffffff; color: #333; margin: 20px; }
    h1 { text-align: center; }
    .container { max-width: 900px; margin: auto; }
    .form-grid { display: grid; grid-template-columns: 1fr 1fr; grid-gap: 15px; padding: 15px; border: 1px solid #ccc; border-radius: 8px; background: #f9f9f9; margin-bottom: 20px; }
    .form-grid label { font-weight: bold; }
    .form-grid p { font-style: italic; margin: 0; }
    .full-width { grid-column: 1 / -1; }
    input[type="number"], select { width: 100%; padding: 8px; box-sizing: border-box; }
    input[type="checkbox"] { transform: scale(1.2); margin-right: 5px; }
    input[type="submit"] { padding: 10px 20px; font-size: 1.1em; background: #3498db; color: #fff; border: none; border-radius: 5px; cursor: pointer; }
    /* Progress Bar Styling */
    #progressContainer { display: none; margin-top: 20px; }
    #progressBarContainer { width: 100%; background: #ccc; border-radius: 5px; overflow: hidden; }
    #progressBar { width: 0%; height: 20px; background: #3498db; }
    #progressText { text-align: center; margin-top: 5px; }
    /* Animation result styling */
    #result { display: flex; justify-content: space-around; align-items: flex-start; margin-top: 20px; }
    #result img { max-width: 60%; height: auto; border: 2px solid #ccc; }
    #summary { max-width: 35%; font-size: 1em; }
    #downloadLink { display: inline-block; margin-top: 10px; padding: 8px 12px; background: #27ae60; color: #fff; text-decoration: none; border-radius: 5px; }
  </style>
</head>
<body>
  <div class="container">
    <h1>Artful Collatz Animation</h1>
    <form id="animationForm">
      <div class="form-grid">
        <div>
          <label for="series_type">Main Series Type:</label>
          <p>(Numbers that feed into Collatz)</p>
          <select id="series_type" name="series_type">
            <option value="fibonacci">Fibonacci</option>
            <option value="primes">Primes</option>
            <option value="triangular">Triangular</option>
            <option value="squares">Squares</option>
            <option value="cubes">Cubes</option>
            <option value="factorials">Factorials</option>
            <option value="powers_of_two">Powers of Two</option>
            <option value="pentagonal">Pentagonal</option>
            <option value="integers">Integers</option>
          </select>
        </div>
        <div>
          <label for="cap">Main Series Length:</label>
          <p>(Number of terms to generate)</p>
          <input type="number" id="cap" name="cap" value="5" min="1">
        </div>
        <div>
          <label for="colormap">Colormap:</label>
          <p>(Color scheme for your art)</p>
          <select id="colormap" name="colormap">
            <option value="viridis">Viridis</option>
            <option value="plasma">Plasma</option>
            <option value="inferno">Inferno</option>
            <option value="magma">Magma</option>
            <option value="cividis">Cividis</option>
          </select>
        </div>
        <div>
          <label for="step_length">Step Length:</label>
          <p>(Distance per step)</p>
          <input type="number" id="step_length" name="step_length" value="10" min="1">
        </div>
        <div>
          <label for="stroke_width">Stroke Width:</label>
          <p>(Line thickness)</p>
          <input type="number" id="stroke_width" name="stroke_width" value="3" min="1" step="0.5">
        </div>
        <div>
          <label for="left_angle">Default Left-turn Angle:</label>
          <p>(For odd numbers)</p>
          <input type="number" id="left_angle" name="left_angle" value="30">
        </div>
        <div>
          <label for="right_angle">Default Right-turn Angle:</label>
          <p>(For even numbers)</p>
          <input type="number" id="right_angle" name="right_angle" value="45">
        </div>
        <div class="full-width">
          <label for="custom_transform">Use Custom Degree Transformation:</label>
          <input type="checkbox" id="custom_transform" name="custom_transform">
          <p>(If enabled: odd turn = (number mod Left Mod), even turn = (number mod Right Mod))</p>
        </div>
        <div>
          <label for="left_mod">Left Mod Value:</label>
          <input type="number" id="left_mod" name="left_mod" value="180">
        </div>
        <div>
          <label for="right_mod">Right Mod Value:</label>
          <input type="number" id="right_mod" name="right_mod" value="180">
        </div>
        <div>
          <label for="consecutive_increment">Consecutive Turn Increment:</label>
          <input type="checkbox" id="consecutive_increment" name="consecutive_increment">
          <p>(Extra degree for consecutive same-parity numbers)</p>
        </div>
        <div>
          <label for="variable_step">Variable Step Length:</label>
          <input type="checkbox" id="variable_step" name="variable_step">
          <p>(Step length increases with each step)</p>
        </div>
        <div>
          <label for="rotation_drift">Rotation Drift (°):</label>
          <p>(Constant drift added each step)</p>
          <input type="number" id="rotation_drift" name="rotation_drift" value="0" step="0.5">
        </div>
        <div>
          <label for="symmetry_mirror">Symmetry Mirror:</label>
          <p>(Mirror drawing)</p>
          <select id="symmetry_mirror" name="symmetry_mirror">
            <option value="None">None</option>
            <option value="Horizontal">Horizontal</option>
            <option value="Vertical">Vertical</option>
          </select>
        </div>
        <div>
          <label for="random_color_variation">Random Color Variation:</label>
          <input type="checkbox" id="random_color_variation" name="random_color_variation">
          <p>(Each sequence gets a random color)</p>
        </div>
        <div>
          <label for="low_quality">Low Quality Rendering:</label>
          <input type="checkbox" id="low_quality" name="low_quality">
          <p>(Faster preview)</p>
        </div>
        <div>
          <label for="dark_background">Dark Background:</label>
          <input type="checkbox" id="dark_background" name="dark_background">
          <p>(For a moody art look)</p>
        </div>
      </div>
      <div style="text-align:center; margin-top:15px;">
        <input type="submit" value="Generate Artful Animation">
      </div>
    </form>
    
    <!-- Progress Bar -->
    <div id="progressContainer">
      <div id="progressBarContainer">
        <div id="progressBar"></div>
      </div>
      <div id="progressText">0%</div>
    </div>
    
    <!-- Animation Result and Summary -->
    <div id="result">
      {% if gif_data %}
        <h2>Animation:</h2>
        <div style="display: flex; justify-content: space-around; align-items: flex-start;">
          <div id="animationContainer">
            <img id="animationImg" src="data:image/gif;base64,{{ gif_data }}" alt="Artful Animation">
            <br><br>
            <a id="downloadLink" href="data:image/gif;base64,{{ gif_data }}" download="animation.gif">Download Animation</a>
          </div>
          <div id="summary">
            <h3>Summary</h3>
            <p>{{ summary }}</p>
          </div>
        </div>
      {% endif %}
    </div>
  </div>
  
  <script>
    // AJAX submission with progress bar update.
    document.getElementById("animationForm").addEventListener("submit", function(e){
      e.preventDefault();
      document.getElementById("progressContainer").style.display = "block";
      var progressBar = document.getElementById("progressBar");
      var progressText = document.getElementById("progressText");
      var progress = 0;
      var interval = setInterval(function(){
        if (progress < 90) {
          progress++;
          progressBar.style.width = progress + "%";
          progressText.innerText = progress + "%";
        }
      }, 100);
      
      var formData = new FormData(document.getElementById("animationForm"));
      fetch("/", { method: "POST", body: formData })
        .then(function(response){ return response.json(); })
        .then(function(json){
          clearInterval(interval);
          progressBar.style.width = "100%";
          progressText.innerText = "100%";
          var resultHTML = '<h2>Animation:</h2>' +
                           '<div style="display: flex; justify-content: space-around; align-items: flex-start;">' +
                           '<div id="animationContainer"><img id="animationImg" src="data:image/gif;base64,' + json.gif_data + '" alt="Artful Animation"><br><br>' +
                           '<a id="downloadLink" href="data:image/gif;base64,' + json.gif_data + '" download="animation.gif">Download Animation</a></div>' +
                           '<div id="summary"><h3>Summary</h3><p>' + json.summary + '</p></div></div>';
          document.getElementById("result").innerHTML = resultHTML;
        })
        .catch(function(error){
          clearInterval(interval);
          progressText.innerText = "Error!";
          console.error(error);
        });
    });
  </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            series_type = request.form.get('series_type', 'fibonacci')
            cap = int(request.form.get('cap', 5))
            colormap = request.form.get('colormap', 'viridis')
            step_length = float(request.form.get('step_length', 10))
            stroke_width = float(request.form.get('stroke_width', 3))
            left_angle = float(request.form.get('left_angle', 30))
            right_angle = float(request.form.get('right_angle', 45))
            custom_transform = request.form.get('custom_transform') == 'on'
            left_mod = float(request.form.get('left_mod', 180))
            right_mod = float(request.form.get('right_mod', 180))
            consecutive_increment = request.form.get('consecutive_increment') == 'on'
            variable_step = request.form.get('variable_step') == 'on'
            rotation_drift = float(request.form.get('rotation_drift', 0))
            symmetry_mirror = request.form.get('symmetry_mirror', 'None')
            random_color_variation = request.form.get('random_color_variation') == 'on'
            low_quality = request.form.get('low_quality') == 'on'
            dark_background = request.form.get('dark_background') == 'on'
            
            # Generate main series from the selected type
            main_series = generate_series(series_type, cap)
            dpi = 50 if low_quality else 100
            
            frames = generate_combined_turtle_animation(
                main_series,
                left_angle,
                right_angle,
                step_length=step_length,
                stroke_width=stroke_width,
                dpi=dpi,
                custom_transform=custom_transform,
                left_mod=left_mod,
                right_mod=right_mod,
                cmap_name=colormap,
                dark_background=dark_background,
                consecutive_increment=consecutive_increment,
                variable_step=variable_step,
                rotation_drift=rotation_drift,
                symmetry_mirror=symmetry_mirror,
                random_color_variation=random_color_variation
            )
            gif_buf = io.BytesIO()
            imageio.mimsave(gif_buf, frames, format='GIF', duration=0.1)
            gif_buf.seek(0)
            gif_data = base64.b64encode(gif_buf.getvalue()).decode('utf-8')
            
            # Build summary of settings (excluding visual style details like color or stroke)
            summary_lines = []
            summary_lines.append(f"Series Type: {series_type.capitalize()} ({cap} terms)")
            if custom_transform:
                summary_lines.append(f"Angle Logic: Custom transform (Left mod: {left_mod}, Right mod: {right_mod})")
            elif consecutive_increment:
                summary_lines.append(f"Angle Logic: Consecutive increment with fixed angles (Left: {left_angle}°, Right: {right_angle}°)")
            else:
                summary_lines.append(f"Angle Logic: Fixed (Left: {left_angle}°, Right: {right_angle}°)")
            if variable_step:
                summary_lines.append("Variable step length enabled")
            if rotation_drift != 0:
                summary_lines.append(f"Rotation drift: {rotation_drift}° per step")
            if symmetry_mirror != "None":
                summary_lines.append(f"Symmetry Mirror: {symmetry_mirror}")
            # (Other toggles like random color, dark background, or low quality can be omitted from summary)
            summary = "<br>".join(summary_lines)
            
            return jsonify({"gif_data": gif_data, "summary": summary})
        except Exception as e:
            return jsonify({"error": str(e)})
    else:
        return render_template_string(template, gif_data=None)

if __name__ == '__main__':
    app.run(debug=True)
