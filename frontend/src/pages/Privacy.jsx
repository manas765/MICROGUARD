import Navbar from "../components/Navbar";

function Privacy() {
  return (
    <div className="min-h-screen bg-cream-50">
      <Navbar />

      <div className="max-w-2xl mx-auto px-4 sm:px-6 py-6 sm:py-10">
        <h1 className="text-lg font-semibold text-indigo-950 mb-2">Data & privacy</h1>
        <p className="text-gray-500 text-sm mb-6">
          A plain explanation of what MICROGUARD collects and how it's protected.
        </p>

        <div className="space-y-4">
          <div className="bg-white rounded-2xl border border-gray-100 p-5">
            <h2 className="font-medium text-indigo-950 mb-2">What we collect</h2>
            <p className="text-sm text-gray-600 leading-relaxed">
              To assess loan applications, we collect your business details, requested loan
              amount and purpose, estimated monthly income, and — if you provide one — a
              guarantor's phone number. We also record the IP address used at signup, which
              helps us detect coordinated fraud attempts.
            </p>
          </div>

          <div className="bg-white rounded-2xl border border-gray-100 p-5">
            <h2 className="font-medium text-indigo-950 mb-2">What's stored as-is</h2>
            <p className="text-sm text-gray-600 leading-relaxed">
              Your business profile, loan application details, and repayment history are
              stored directly, since loan officers need to review them to make decisions —
              this is visible only to you and authorized loan officers/admins.
            </p>
          </div>

          <div className="bg-white rounded-2xl border border-gray-100 p-5">
            <h2 className="font-medium text-indigo-950 mb-2">What's hashed, not stored raw</h2>
            <p className="text-sm text-gray-600 leading-relaxed">
              When a fraud check is logged in our tamper-evident audit trail, your guarantor's
              phone number is converted into a one-way hash before it's written — a fingerprint
              that lets us detect if the same guarantor appears across multiple applications,
              without storing the actual phone number in that log. The hash can't be reversed
              back into the original number.
            </p>
          </div>

          <div className="bg-white rounded-2xl border border-gray-100 p-5">
            <h2 className="font-medium text-indigo-950 mb-2">The audit trail</h2>
            <p className="text-sm text-gray-600 leading-relaxed">
              Key events — loan approvals, rejections, repayments, and fraud flags — are
              recorded in a hash-chained log, where each entry is cryptographically linked to
              the one before it. This makes the history tamper-evident: any attempt to alter a
              past record would break the chain and be detectable.
            </p>
          </div>

          <div className="bg-white rounded-2xl border border-gray-100 p-5">
            <h2 className="font-medium text-indigo-950 mb-2">Who can see what</h2>
            <p className="text-sm text-gray-600 leading-relaxed">
              You can always see your own applications and repayment status. Loan officers and
              admins can view all applications and the fraud-detection graph in order to make
              lending decisions, but the audit log and fraud graph are not visible to other
              borrowers.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Privacy;