export default function AdminClientEntry() {
  const submit = e => {
    e.preventDefault();
    const reader = new FileReader();

    reader.onload = async () => {
      await fetch('http://localhost:5000/api/client', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company_name: e.target.name.value,
          description: e.target.desc.value,
          logo: reader.result
        })
      });
      alert('Client Added');
    };

    reader.readAsDataURL(e.target.logo.files[0]);
  };

  return (
    <form onSubmit={submit} className="container">
      <h2>Add Client</h2>
      <input name="name" placeholder="Company Name" required />
      <textarea name="desc" placeholder="Company Description" required />
      <input type="file" name="logo" required />
      <button>Add Client</button>
    </form>
  );
}
