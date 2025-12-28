export default function Enquire() {
const submit = async e => {
e.preventDefault();
const data = {
name: e.target.name.value,
email: e.target.email.value,
message: e.target.message.value
};
await fetch('http://localhost:5000/api/enquire', {
method: 'POST',
headers: { 'Content-Type': 'application/json' },
body: JSON.stringify(data)
});
alert('Enquiry Sent');
};


return (
<form onSubmit={submit}>
<input name='name' placeholder='Name' />
<input name='email' placeholder='Email' />
<textarea name='message' />
<button>Submit</button>
</form>
);
}