import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ShieldCheck, Network, DatabaseBackup, Briefcase } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {}
      <section className="container mx-auto px-6 py-20 text-center">
        <motion.h1
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-4xl md:text-5xl font-bold text-slate-800"
        >
          Welcome to <span className="text-blue-600">Cyber IT</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="mt-6 text-lg text-slate-600 max-w-2xl mx-auto"
        >
          Cyber IT provides professional cybersecurity and IT solutions to help
          businesses protect, manage, and grow their digital assets.
        </motion.p>

        <div className="mt-8 flex justify-center gap-4">
          <Link
            to="/services"
            className="px-6 py-3 rounded-2xl bg-blue-600 text-white shadow hover:bg-blue-700 transition"
          >
            Our Services
          </Link>
          <Link
            to="/contact"
            className="px-6 py-3 rounded-2xl bg-white text-blue-600 border border-blue-200 shadow hover:bg-blue-50 transition"
          >
            Contact Us
          </Link>
        </div>
      </section>

      {/* Services Section */}
      <section className="container mx-auto px-6 pb-20">
        <h2 className="text-3xl font-semibold text-center text-slate-800 mb-12">
          Our Services
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <ServiceCard
            icon={<ShieldCheck className="h-8 w-8 text-blue-600" />}
            title="Cyber Security Solutions"
            description="Protect your systems from modern cyber threats with advanced security solutions."
          />
          <ServiceCard
            icon={<Network className="h-8 w-8 text-blue-600" />}
            title="Network Protection"
            description="Secure and monitor your network infrastructure for maximum reliability."
          />
          <ServiceCard
            icon={<DatabaseBackup className="h-8 w-8 text-blue-600" />}
            title="Data Security & Backup"
            description="Ensure data integrity with secure storage, backups, and recovery plans."
          />
          <ServiceCard
            icon={<Briefcase className="h-8 w-8 text-blue-600" />}
            title="IT Consulting"
            description="Expert guidance to optimize IT strategy, infrastructure, and operations."
          />
        </div>
      </section>
    </div>
  );
}

function ServiceCard({ icon, title, description }) {
  return (
    <motion.div
      whileHover={{ y: -5 }}
      className="bg-white rounded-2xl p-6 shadow-sm hover:shadow-md transition"
    >
      <div className="mb-4">{icon}</div>
      <h3 className="text-lg font-semibold text-slate-800 mb-2">{title}</h3>
      <p className="text-slate-600 text-sm">{description}</p>
    </motion.div>
  );
}
