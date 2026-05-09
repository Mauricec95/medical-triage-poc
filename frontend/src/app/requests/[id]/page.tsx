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

const STATUS_OPTIONS = [
  { value: "complet", label: "Complet" },
  { value: "incomplet", label: "Incomplet" },
  { value: "a_valider", label: "À valider" },
  { value: "route", label: "Routé" },
];

function EditableField({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div>
      <label className="block text-xs font-medium text-gray-500 mb-0.5">
        {label}
      </label>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full border border-gray-300 rounded px-2 py-1 text-sm focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
        placeholder="—"
      />
    </div>
  );
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
  const [saving, setSaving] = useState(false);
  const [saveMsg, setSaveMsg] = useState<string | null>(null);
  const [reqData, setReqData] = useState<Record<string, unknown>>({});
  const [currentStatus, setCurrentStatus] = useState("");

  const fetchData = useCallback(() => {
    fetch(`${API_URL}/requests/${id}`)
      .then((res) => res.json())
      .then((d) => {
        setData(d);
        setReqData(d.request || {});
        setCurrentStatus(d.status);
        setAckMessage(
          (d.request as Record<string, string>)?.ack_message_fr || ""
        );
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [id]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const updateField = (
    section: string,
    field: string,
    value: string | boolean | null
  ) => {
    setReqData((prev) => ({
      ...prev,
      [section]: {
        ...(prev[section] as Record<string, unknown>),
        [field]: value,
      },
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    setSaveMsg(null);
    try {
      const body: Record<string, unknown> = { request: reqData };
      if (currentStatus !== data?.status) {
        body.status = currentStatus;
      }
      const res = await fetch(`${API_URL}/requests/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (res.ok) {
        setSaveMsg("Modifications enregistrées");
        fetchData();
        setTimeout(() => setSaveMsg(null), 3000);
      } else {
        setSaveMsg("Erreur lors de la sauvegarde");
      }
    } finally {
      setSaving(false);
    }
  };

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
    return (
      <div className="flex items-center justify-center py-16">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        <span className="ml-3 text-gray-500">Chargement…</span>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center py-16">
        <p className="text-red-500 text-lg">Demande non trouvée.</p>
        <Link href="/" className="text-blue-600 hover:text-blue-800 text-sm mt-2 inline-block">
          Retour à la liste
        </Link>
      </div>
    );
  }

  const patient = (reqData.patient || {}) as Record<string, string | null>;
  const prescriber = (reqData.prescriber || {}) as Record<
    string,
    string | null
  >;
  const exam = (reqData.exam || {}) as Record<string, unknown>;
  const missingFields = (reqData.missing_fields || []) as Array<
    Record<string, string>
  >;
  const routing = (reqData.routing || {}) as Record<string, string | null>;
  const source = (reqData.source || {}) as Record<string, string | null>;

  return (
    <div>
      {/* Top bar */}
      <div className="flex items-center justify-between mb-6">
        <Link
          href="/"
          className="text-blue-600 hover:text-blue-800 text-sm inline-flex items-center gap-1"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-4 w-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M15 19l-7-7 7-7"
            />
          </svg>
          Retour à la liste
        </Link>
        <div className="flex items-center gap-3">
          <select
            value={currentStatus}
            onChange={(e) => setCurrentStatus(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-1.5 text-sm bg-white"
          >
            {STATUS_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <button
            onClick={handleSave}
            disabled={saving}
            className="inline-flex items-center gap-1 bg-green-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-green-700 disabled:opacity-50"
          >
            {saving ? "Enregistrement…" : "Enregistrer"}
          </button>
          {saveMsg && (
            <span className="text-sm text-green-700">{saveMsg}</span>
          )}
        </div>
      </div>

      {/* Two-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: raw text */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={1.5}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
              />
            </svg>
            Texte original
          </h3>
          <p className="text-xs text-gray-500 mb-2">
            Source : {data.source_filename || "—"} | Reçu le{" "}
            {new Date(data.created_at).toLocaleDateString("fr-FR", {
              day: "2-digit",
              month: "long",
              year: "numeric",
              hour: "2-digit",
              minute: "2-digit",
            })}
          </p>
          <pre className="bg-gray-50 p-4 rounded text-sm whitespace-pre-wrap font-mono max-h-[500px] overflow-y-auto border border-gray-200">
            {(source.raw_text as string) || "(Aucun texte)"}
          </pre>
        </div>

        {/* Right: editable structured form */}
        <div className="bg-white rounded-lg shadow p-6 space-y-5">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={1.5}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10"
              />
            </svg>
            Informations extraites
          </h3>

          {/* Patient */}
          <section className="border border-gray-100 rounded-lg p-4 bg-gray-50">
            <h4 className="font-medium text-gray-700 mb-3 text-sm uppercase tracking-wide">
              Patient
            </h4>
            <div className="grid grid-cols-2 gap-3">
              <EditableField
                label="Nom complet"
                value={patient.full_name || ""}
                onChange={(v) => updateField("patient", "full_name", v)}
              />
              <EditableField
                label="Date de naissance"
                value={patient.dob || ""}
                onChange={(v) => updateField("patient", "dob", v)}
              />
              <EditableField
                label="Sexe"
                value={patient.sex || ""}
                onChange={(v) => updateField("patient", "sex", v)}
              />
              <EditableField
                label="Téléphone"
                value={patient.phone || ""}
                onChange={(v) => updateField("patient", "phone", v)}
              />
              <EditableField
                label="Email"
                value={patient.email || ""}
                onChange={(v) => updateField("patient", "email", v)}
              />
            </div>
          </section>

          {/* Prescriber */}
          <section className="border border-gray-100 rounded-lg p-4 bg-gray-50">
            <h4 className="font-medium text-gray-700 mb-3 text-sm uppercase tracking-wide">
              Prescripteur
            </h4>
            <div className="grid grid-cols-2 gap-3">
              <EditableField
                label="Nom complet"
                value={prescriber.full_name || ""}
                onChange={(v) => updateField("prescriber", "full_name", v)}
              />
              <EditableField
                label="Spécialité"
                value={prescriber.specialty || ""}
                onChange={(v) => updateField("prescriber", "specialty", v)}
              />
              <EditableField
                label="Service"
                value={prescriber.service || ""}
                onChange={(v) => updateField("prescriber", "service", v)}
              />
              <EditableField
                label="Téléphone"
                value={prescriber.phone || ""}
                onChange={(v) => updateField("prescriber", "phone", v)}
              />
              <EditableField
                label="Email"
                value={prescriber.email || ""}
                onChange={(v) => updateField("prescriber", "email", v)}
              />
            </div>
          </section>

          {/* Exam */}
          <section className="border border-gray-100 rounded-lg p-4 bg-gray-50">
            <h4 className="font-medium text-gray-700 mb-3 text-sm uppercase tracking-wide">
              Examen
            </h4>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-0.5">
                  Modalité
                </label>
                <select
                  value={(exam.modality as string) || ""}
                  onChange={(e) =>
                    updateField(
                      "exam",
                      "modality",
                      e.target.value || null
                    )
                  }
                  className="w-full border border-gray-300 rounded px-2 py-1 text-sm bg-white"
                >
                  <option value="">—</option>
                  <option value="scanner">Scanner</option>
                  <option value="IRM">IRM</option>
                  <option value="doppler">Doppler</option>
                  <option value="echo">Écho</option>
                  <option value="radio">Radio</option>
                  <option value="autre">Autre</option>
                </select>
              </div>
              <EditableField
                label="Région"
                value={(exam.region as string) || ""}
                onChange={(v) => updateField("exam", "region", v)}
              />
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-0.5">
                  Injection
                </label>
                <select
                  value={
                    exam.with_injection === true
                      ? "true"
                      : exam.with_injection === false
                        ? "false"
                        : ""
                  }
                  onChange={(e) => {
                    const v = e.target.value;
                    updateField(
                      "exam",
                      "with_injection",
                      v === "true" ? true : v === "false" ? false : null
                    );
                  }}
                  className="w-full border border-gray-300 rounded px-2 py-1 text-sm bg-white"
                >
                  <option value="">Inconnu</option>
                  <option value="true">Oui</option>
                  <option value="false">Non</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-0.5">
                  Urgence
                </label>
                <select
                  value={(exam.urgency as string) || "routine"}
                  onChange={(e) =>
                    updateField("exam", "urgency", e.target.value)
                  }
                  className="w-full border border-gray-300 rounded px-2 py-1 text-sm bg-white"
                >
                  <option value="routine">Routine</option>
                  <option value="prioritaire">Prioritaire</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>
            </div>
          </section>

          {/* Clinical indication */}
          <section className="border border-gray-100 rounded-lg p-4 bg-gray-50">
            <h4 className="font-medium text-gray-700 mb-2 text-sm uppercase tracking-wide">
              Indication clinique
            </h4>
            <textarea
              value={(reqData.clinical_indication as string) || ""}
              onChange={(e) =>
                setReqData((prev) => ({
                  ...prev,
                  clinical_indication: e.target.value,
                }))
              }
              className="w-full border border-gray-300 rounded px-2 py-1 text-sm h-16 resize-y"
              placeholder="Indication clinique…"
            />
          </section>

          {/* Missing fields */}
          {missingFields.length > 0 && (
            <section>
              <h4 className="font-medium text-red-700 mb-2 flex items-center gap-1">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
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
                    <div className="text-red-700 text-xs mt-0.5">
                      {mf.reason}
                    </div>
                    <div className="text-red-600 italic mt-1 text-xs">
                      &laquo; {mf.suggested_question_fr} &raquo;
                    </div>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {/* Routing */}
          <section className="border border-gray-100 rounded-lg p-4 bg-gray-50">
            <h4 className="font-medium text-gray-700 mb-2 text-sm uppercase tracking-wide">
              Routage
            </h4>
            <div className="text-sm space-y-1">
              <div className="flex gap-2">
                <span className="text-gray-500 min-w-[70px]">Action :</span>
                <span className="font-medium">
                  {routing.next_action
                    ?.replace(/_/g, " ")
                    .replace(/\b\w/g, (c) => c.toUpperCase()) || "—"}
                </span>
              </div>
              <div className="flex gap-2">
                <span className="text-gray-500 min-w-[70px]">Contact :</span>
                <span>{routing.target_contact || "—"}</span>
              </div>
              <div className="flex gap-2">
                <span className="text-gray-500 min-w-[70px]">Motif :</span>
                <span>{routing.rationale_fr || "—"}</span>
              </div>
            </div>
          </section>

          {/* Confidence */}
          <section className="border border-gray-100 rounded-lg p-4 bg-gray-50">
            <h4 className="font-medium text-gray-700 mb-2 text-sm uppercase tracking-wide">
              Confiance
            </h4>
            <div className="flex items-center gap-3">
              <div className="flex-1 bg-gray-200 rounded-full h-2.5">
                <div
                  className={`h-2.5 rounded-full ${
                    ((reqData.confidence as number) || 0) >= 0.8
                      ? "bg-green-500"
                      : ((reqData.confidence as number) || 0) >= 0.5
                        ? "bg-yellow-500"
                        : "bg-red-500"
                  }`}
                  style={{
                    width: `${((reqData.confidence as number) || 0) * 100}%`,
                  }}
                />
              </div>
              <span className="text-sm font-medium text-gray-700 w-12 text-right">
                {(((reqData.confidence as number) || 0) * 100).toFixed(0)} %
              </span>
            </div>
          </section>
        </div>
      </div>

      {/* Acknowledgement message */}
      <div className="mt-6 bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={1.5}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75"
            />
          </svg>
          Accusé de réception
        </h3>
        <textarea
          value={ackMessage}
          onChange={(e) => setAckMessage(e.target.value)}
          className="w-full border border-gray-300 rounded-md p-3 text-sm font-mono h-48 resize-y focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
        />
        <div className="mt-3 flex items-center gap-3">
          <button
            onClick={handleSendAck}
            disabled={sending || data.status === "route"}
            className="inline-flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5"
              />
            </svg>
            {sending
              ? "Envoi en cours…"
              : data.status === "route"
                ? "Déjà envoyé"
                : "Envoyer (mock)"}
          </button>
          <span className="text-xs text-gray-500">
            L&apos;envoi est simulé — le message est affiché dans la console du
            backend.
          </span>
        </div>
      </div>
    </div>
  );
}
