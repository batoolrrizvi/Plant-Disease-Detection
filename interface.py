import os
import uuid
import shutil
import pandas as pd
from flask import Flask, request, render_template_string, url_for

# ─── CONFIG ───────────────────────────────────────────────────────────────────
ALLOWED_EXT    = {'png', 'jpg', 'jpeg'}
CSV_PATH       = 'results_with_infected_area_all_splits.csv'
SEG_MASK_ROOT  = os.path.join('Segmented', 'masks')
STATIC_RES     = 'static/results'
UPLOAD_DIR     = 'static/uploads'

os.makedirs(STATIC_RES, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

df = pd.read_csv(CSV_PATH)
app = Flask(__name__)

# ─── ENHANCED UPLOAD PAGE WITH CREDITS ─────────────────────────────────────────
UPLOAD_HTML = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Plant Disease Detection</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
  <div class="container py-5">
    <div class="card mx-auto" style="max-width:420px;">
      <div class="card-body text-center">
        <h3 class="card-title text-success mb-4">Plant Disease Detection</h3>
        <form method="post" enctype="multipart/form-data">
          <input class="form-control mb-3" type="file" name="image" accept=".jpg,.jpeg,.png">
          <button class="btn btn-success w-100">Lookup</button>
        </form>
        {% if error %}
          <div class="alert alert-danger mt-3">{{ error }}</div>
        {% endif %}
      </div>
    </div>
    <p class="text-center text-muted mt-4">
      Made by Rameen Babar, Arisha Khan, Batool Rizvi
    </p>
  </div>
</body>
</html>
'''

# ─── RESULT PAGE WITH D3 GAUGE & DISEASE NAME ─────────────────────────────────
RESULT_HTML = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Lookup Result</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <script src="https://d3js.org/d3.v7.min.js"></script>
</head>
<body class="bg-light">
  <div class="container py-5">
    <div class="card mx-auto" style="max-width:800px;">
      <div class="card-header bg-success text-white">
        <h4 class="mb-0">Computed Infection Result</h4>
      </div>
      <div class="card-body">
        <div class="mb-4 text-center">
          <h5>Disease: <span class="text-danger">{{ label.replace('_', ' ') }}</span></h5>
        </div>
        <div class="row gx-4">
          <div class="col-md-4 text-center">
            <h6>Original Leaf</h6>
            <img src="{{ orig_url }}" class="img-fluid rounded border" alt="Input">
          </div>
          <div class="col-md-4 text-center">
            <h6>Lesion Mask</h6>
            <img src="{{ mask_url }}" class="img-fluid rounded border" alt="Mask">
          </div>
          <div class="col-md-4 text-center">
            <h6>Infection Gauge</h6>
            <div id="gauge"></div>
          </div>
        </div>
        <div class="text-center mt-4">
          <a href="/" class="btn btn-primary">Analyze Another</a>
        </div>
      </div>
    </div>
  </div>

  <script>
// D3 gauge
const pct = {{ pct }};
const width = 200, height = 120;
const twoPi = 2 * Math.PI;
const arc = d3.arc()
  .startAngle(-Math.PI/2)
  .endAngle(-Math.PI/2 + twoPi * pct/100)
  .innerRadius(50)
  .outerRadius(70);

const svg = d3.select("#gauge")
  .append("svg")
    .attr("width", width).attr("height", height)
  .append("g")
    .attr("transform", `translate(${width/2},${height})`);

svg.append("path")
    .attr("d", arc)
    .attr("fill", "tomato");

svg.append("text")
    .attr("text-anchor", "middle")
    .attr("dy", "-0.5em")
    .style("font-size", "1.2em")
    .text(pct.toFixed(1) + "%");
  </script>

</body>
</html>
'''

@app.route('/', methods=['GET','POST'])
def index():
    error = None
    if request.method == 'POST':
        f = request.files.get('image')
        if not f:
            error = "Please select a file."
        else:
            ext = f.filename.rsplit('.',1)[-1].lower()
            if ext not in ALLOWED_EXT:
                error = "Invalid file type."
        if error:
            return render_template_string(UPLOAD_HTML, error=error)

        fname = f.filename
        base, _ = os.path.splitext(fname)
        upload_name = f"{uuid.uuid4().hex}_{fname}"
        upload_path = os.path.join(UPLOAD_DIR, upload_name)
        f.save(upload_path)
        orig_url = url_for('static', filename=f"uploads/{upload_name}")

        row = df[df['filename'] == fname]
        if row.empty:
            error = f'Filename "{fname}" not in records.'
            return render_template_string(UPLOAD_HTML, error=error)

        label = row.iloc[0]['label']
        pct   = float(row.iloc[0]['infected_pct_leaf'])

        mask_src = os.path.join(SEG_MASK_ROOT, label, f"{base}_mask.png")
        if not os.path.exists(mask_src):
            error = f"Mask not found for {fname}."
            return render_template_string(UPLOAD_HTML, error=error)

        dest_name = f"{uuid.uuid4().hex}_mask.png"
        dest_path = os.path.join(STATIC_RES, dest_name)
        shutil.copy(mask_src, dest_path)
        mask_url = url_for('static', filename=f"results/{dest_name}")

        return render_template_string(
            RESULT_HTML,
            label=label,
            pct=pct,
            orig_url=orig_url,
            mask_url=mask_url
        )

    return render_template_string(UPLOAD_HTML, error=error)

if __name__=='__main__':
    app.run(debug=True)
