const express = require('express');
const db = require('./db');
const nodemailer = require('nodemailer');
const multer = require('multer');
const path = require('path');

const router = express.Router();

const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, path.join(__dirname, 'uploads')),
  filename: (req, file, cb) => cb(null, Date.now() + '_' + file.originalname)
});
const upload = multer({ storage });

router.use('/uploads', express.static(path.join(__dirname, 'uploads')));

const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: 'mca25.yadav.anurag@gnims.com',
    pass: 'qlzyxtwifkwbexlg'
  }
});

router.post('/enquire', (req, res) => {
  const { name, email, message } = req.body;
  db.query('INSERT INTO enquiries VALUES (NULL,?,?,?)', [name, email, message], err => {
    if (err) return res.status(500).json({ status: 'Error' });
    transporter.sendMail({
      to: 'mca25.yadav.anurag@gnims.com',
      subject: 'New Enquiry',
      text: `Name: ${name}\nEmail: ${email}\nMessage: ${message}`
    });
    res.json({ status: 'Enquiry Sent' });
  });
});

router.get('/enquiries', (req, res) => {
  db.query('SELECT * FROM enquiries', (err, result) => {
    if (err) return res.status(500).json([]);
    res.json(result);
  });
});

router.post('/client', (req, res) => {
  const { company_name, description, logo } = req.body;
  db.query(
    'INSERT INTO clients VALUES (NULL,?,?,?)',
    [company_name, description, logo],
    err => {
      if (err) return res.status(500).json({ status: 'Error' });
      res.json({ status: 'Client Added' });
    }
  );
});

router.get('/clients', (req, res) => {
  db.query('SELECT id, company_name, description, logo FROM clients', (err, result) => {
    if (err) return res.json([]);
    res.json(result);
  });
});

router.post('/login', (req, res) => {
  const { username, password } = req.body;
  db.query(
    'SELECT * FROM admin WHERE username=? AND password=?',
    [username, password],
    (err, result) => {
      if (err) return res.status(500).json(false);
      res.json(result.length > 0);
    }
  );
});

router.get('/jobs', (req, res) => {
  db.query('SELECT id, job_title, job_description, location FROM jobs', (err, result) => {
    if (err) return res.status(500).json([]);
    res.json(result);
  });
});

router.post('/jobs', (req, res) => {
  const { job_title, job_description, location } = req.body;
  db.query(
    'INSERT INTO jobs (job_title, job_description, location) VALUES (?,?,?)',
    [job_title, job_description, location],
    err => {
      if (err) return res.status(500).json({ status: 'Error' });
      res.json({ status: 'Job Added' });
    }
  );
});

router.post(
  '/apply',
  upload.fields([
    { name: 'photo', maxCount: 1 },
    { name: 'resume', maxCount: 1 }
  ]),
  (req, res) => {
    const { name, email, phone, job_title } = req.body;

    if (!req.files || !req.files.photo || !req.files.resume) {
      return res.status(400).json({ status: 'Files missing' });
    }

    const photo = req.files.photo[0].buffer;
    const resumePath = '/api/uploads/' + req.files.resume[0].filename;

    db.query(
      'INSERT INTO job_applications (name, email, phone, job_title, photo, resume_path) VALUES (?,?,?,?,?,?)',
      [name, email, phone, job_title, photo, resumePath],
      err => {
        if (err) {
          console.error('Insert Application Error:', err);
          return res.status(500).json({ status: 'Error' });
        }
        res.json({ status: 'Applied' });
      }
    );
  }
);

router.get('/applications', (req, res) => {
  db.query('SELECT * FROM job_applications', (err, result) => {
    if (err) return res.status(500).json([]);
    res.json(result);
  });
});

router.post('/applications/status', (req, res) => {
  const { id, status, email } = req.body;
  db.query('UPDATE job_applications SET status=? WHERE id=?', [status, id], err => {
    if (err) return res.status(500).json({ status: 'Error' });
    transporter.sendMail({
      to: email,
      subject: 'CYBER IT Job Application Status',
      text: `Your application has been ${status}. Thank you for applying to CYBER IT.`
    });
    res.json({ status: 'Updated' });
  });
});

module.exports = router;
