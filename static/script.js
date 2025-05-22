document.getElementById('videoForm').addEventListener('submit', async (e) => {
  e.preventDefault();

  const url = document.getElementById('url').value.trim();
  const resultDiv = document.getElementById('result');
  const errorDiv = document.getElementById('error');

  resultDiv.classList.add('hidden');
  errorDiv.classList.add('hidden');
  errorDiv.textContent = '';

  try {
    const res = await fetch(`/cgi-bin/backend.py?url=${encodeURIComponent(url)}`);
    const data = await res.json();

    if (data.error) {
      throw new Error(data.error);
    }

    document.getElementById('title').textContent = data.title;
    document.getElementById('uploader').textContent = data.uploader;
    document.getElementById('views').textContent = data.views;
    document.getElementById('upload_date').textContent = formatDate(data.upload_date);
    document.getElementById('duration').textContent = data.duration;
    document.getElementById('thumbnail').src = data.thumbnail;

    resultDiv.classList.remove('hidden');
  } catch (err) {
    errorDiv.textContent = `Error: ${err.message}`;
    errorDiv.classList.remove('hidden');
  }
});

function formatDate(yyyymmdd) {
  if (!/^\d{8}$/.test(yyyymmdd)) return yyyymmdd;
  return `${yyyymmdd.slice(0, 4)}-${yyyymmdd.slice(4, 6)}-${yyyymmdd.slice(6)}`;
}
