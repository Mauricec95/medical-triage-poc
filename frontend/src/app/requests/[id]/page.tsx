"use client";

import Link from "next/link";
import { use, useCallback, useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface RequestDetail {
  id: string;
  status: string;
  source_filename: string | null;
  created_at: string;
  updated_at: string;
  request: Record<string, unknown>;
}

export default function RequestDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const [data, setData] = useState<RequestDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [ackMessage, setAckMessage] = useState("");
  const [sending, setSending] = useState(false);

  const fetchData = useCallback(() => {
    fetch(`${API_URL}/requests/${id}`)
      .then((res) => res.json())
      .then((d) => {
        setData(d);
        const req = d.request || {};
        setAckMessage(
          (req as Record<string, string>).ack_message_fr || ""
        );
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [id]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleSendAck = async () => {
    if (!data) return;
    setSending(true);
    try {
      const res = await fetch(`${API_URL}/requests/${id}/send-ack`, {
        method: "POST",
      });
      if (res.ok) {
        fetchData();
      }
    } finally {
      setSending(false);
    }
  };

  if (loading) {
    return <p className="text-gray-500">Chargement...</p>;
  }

  if (!data) {
    return <p className="text-red-500">Demande non trouvee.</p>;
  }

  const req = (data.request || {}) as Record<string, unknown>;
  const patient = (req.patient || {}) as Record<string, string | null>;
  const prescriber = (req.prescriber || {}) as Record<string, string | null>;
  const exam = (req.exam || {}) as Record<string, unknown>;
  const missingFields = (req.missing_fields || []) as Array<
    Record<string, string>
  >;
  const routing = (req.routing || {}) as Record<string, string | null>;
  const source = (req.source || {}) as Record<string, string | null>;

  return (
    <div>
      <div className="mb-6">
        <Link
          href="/"
          className="text-blue-600 hover:text-blue-800 text-sm"
        >
          &larr; Retour a la liste
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: raw text */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Texte original</h3>
          <p className="text-sm text-gray-500 mb-2">
            Source : {data.source_filename || "—"}
          </p>
          <pre className="bg-gray-50 p-4 rounded text-sm whitespace-pre-wrap font-mono max-h-96 overflow-y-auto">
            {(source.raw_text as string) || "(Aucun texte)"}
          </pre>
        </div>

        {/* Right: structured form */}
        <div className="bg-white rounded-lg shadow p-6 space-y-6">
          <h3 className="text-lg font-semibold">Informations extraites</h3>

          {/* Patient */}
          <section>
            <h4 className="font-medium text-gray-700 mb-2">Patient</h4>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="text-gray-500">Nom :</span>{" "}
                {patient.full_name || "—"}
              </div>
              <div>
                <span className="text-gray-500">DDN :</span>{" "}
                {patient.dob || "—"}
              </div>
              <div>
                <span className="text-gray-500">Sexe :</span>{" "}
                {patient.sex || "—"}
              </div>
              <div>
                <span className="text-gray-500">Tel :</span>{" "}
                {patient.phone || "—"}
              </div>
              <div>
                <span className="text-gray-500">Email :</span>{" "}
                {patient.email || "—"}
              </div>
            </div>
          </section>

          {/* Prescriber */}
          <section>
            <h4 className="font-medium text-gray-700 mb-2">Prescripteur</h4>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="text-gray-500">Nom :</span>{" "}
                {prescriber.full_name || "—"}
              </div>
              <div>
                <span className="text-gray-500">Specialite :</span>{" "}
                {prescriber.specialty || "—"}
              </div>
              <div>
                <span className="text-gray-500">Service :</span>{" "}
                {prescriber.service || "—"}
              </div>
              <div>
                <span className="text-gray-500">Tel :</span>{" "}
                {prescriber.phone || "—"}
              </div>
              <div>
                <span className="text-gray-500">Email :</span>{" "}
                {prescriber.email || "—"}
              </div>
            </div>
          </section>

          {/* Exam */}
          <section>
            <h4 className="font-medium text-gray-700 mb-2">Examen</h4>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="text-gray-500">Modalite :</span>{" "}
                {(exam.modality as string) || "—"}
              </div>
              <div>
                <span className="text-gray-500">Region :</span>{" "}
                {(exam.region as string) || "—"}
              </div>
              <div>
                <span className="text-gray-500">Injection :</span>{" "}
                {exam.with_injection === true
                  ? "Oui"
                  : exam.with_injection === false
                    ? "Non"
                    : "Inconnu"}
              </div>
              <div>
                <span className="text-gray-500">Urgence :</span>{" "}
                {(exam.urgency as string) || "routine"}
              </div>
            </div>
            {typeof exam.protocol_notes === "string" &&
              exam.protocol_notes && (
                <p className="text-sm mt-1 text-gray-600">
                  Notes : {exam.protocol_notes}
                </p>
              )}
          </section>

          {/* Clinical indication */}
          <section>
            <h4 className="font-medium text-gray-700 mb-2">
              Indication clinique
            </h4>
            <p className="text-sm">
              {(req.clinical_indication as string) || "—"}
            </p>
          </section>

          {/* Missing fields */}
          {missingFields.length > 0 && (
            <section>
              <h4 className="font-medium text-red-700 mb-2">
                Champs manquants ({missingFields.length})
              </h4>
              <ul className="space-y-2">
                {missingFields.map((mf, i) => (
                  <li
                    key={i}
                    className="bg-red-50 border border-red-200 rounded p-3 text-sm"
                  >
                    <div className="font-medium text-red-800">
                      {mf.field_path}
                    </div>
                    <div className="text-red-700">{mf.reason}</div>
                    <div className="text-red-600 italic mt-1">
                      {mf.suggested_question_fr}
                    </div>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {/* Routing */}
          <section>
            <h4 className="font-medium text-gray-700 mb-2">Routage</h4>
            <div className="text-sm space-y-1">
              <div>
                <span className="text-gray-500">Action :</span>{" "}
                {routing.next_action || "—"}
              </div>
              <div>
                <span className="text-gray-500">Contact :</span>{" "}
                {routing.target_contact || "—"}
              </div>
              <div>
                <span className="text-gray-500">Motif :</span>{" "}
                {routing.rationale_fr || "—"}
              </div>
            </div>
          </section>

          {/* Confidence */}
          <section>
            <h4 className="font-medium text-gray-700 mb-2">Confiance</h4>
            <div className="flex items-center gap-2">
              <div className="flex-1 bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full"
                  style={{
                    width: `${((req.confidence as number) || 0) * 100}%`,
                  }}
                />
              </div>
              <span className="text-sm text-gray-600">
                {(((req.confidence as number) || 0) * 100).toFixed(0)}%
              </span>
            </div>
          </section>
        </div>
      </div>

      {/* Acknowledgement message */}
      <div className="mt-6 bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">
          Accuse de reception
        </h3>
        <textarea
          value={ackMessage}
          onChange={(e) => setAckMessage(e.target.value)}
          className="w-full border border-gray-300 rounded-md p-3 text-sm font-mono h-48 resize-y"
        />
        <div className="mt-3 flex items-center gap-3">
          <button
            onClick={handleSendAck}
            disabled={sending}
            className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {sending ? "Envoi en cours..." : "Envoyer (mock)"}
          </button>
          <span className="text-xs text-gray-500">
            L&apos;envoi est simule — le message est affiche dans la console du
            backend.
          </span>
        </div>
      </div>
    </div>
  );
}
