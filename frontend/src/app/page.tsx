"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface RequestSummary {
  id: string;
  status: string;
  source_filename: string | null;
  created_at: string;
  patient_name: string | null;
  modality: string | null;
  urgency: string | null;
  missing_count: number;
}

const STATUS_LABELS: Record<string, { label: string; color: string }> = {
  complet: { label: "Complet", color: "bg-green-100 text-green-800 border-green-300" },
  incomplet: { label: "Incomplet", color: "bg-orange-100 text-orange-800 border-orange-300" },
  a_valider: { label: "À valider", color: "bg-blue-100 text-blue-800 border-blue-300" },
  route: { label: "Routé", color: "bg-purple-100 text-purple-800 border-purple-300" },
};

const MODALITY_LABELS: Record<string, string> = {
  scanner: "Scanner",
  IRM: "IRM",
  doppler: "Doppler",
  echo: "Écho",
  radio: "Radio",
  autre: "Autre",
};

const STATUS_FILTERS = [
  { value: "", label: "Toutes" },
  { value: "incomplet", label: "Incomplet" },
  { value: "a_valider", label: "À valider" },
  { value: "route", label: "Routé" },
  { value: "nouveau", label: "Nouveau" },
];

const MODALITY_FILTERS = [
  { value: "radio", label: "radio" },
  { value: "IRM", label: "IRM" },
  { value: "scanner", label: "scanner" },
  { value: "doppler", label: "doppler" },
  { value: "echo", label: "echo" },
];

export default function InboxPage() {
  const [requests, setRequests] = useState<RequestSummary[]>([]);
  const [allRequests, setAllRequests] = useState<RequestSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState<string>("");
  const [filterModality, setFilterModality] = useState<string>("");
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchRequests = () => {
    const params = new URLSearchParams();
    if (filterStatus) params.set("status", filterStatus);
    if (filterModality) params.set("modality", filterModality);

    fetch(`${API_URL}/requests?${params}`)
      .then((res) => res.json())
      .then((data) => {
        setRequests(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  const fetchAllRequests = () => {
    fetch(`${API_URL}/requests`)
      .then((res) => res.json())
      .then((data) => setAllRequests(data))
      .catch(() => {});
  };

  useEffect(() => {
    fetchRequests();
    fetchAllRequests();
  }, [filterStatus, filterModality]);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setUploadError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_URL}/ingest`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error(`Erreur ${res.status}`);
      fetchRequests();
      fetchAllRequests();
    } catch (err) {
      setUploadError(
        err instanceof Error ? err.message : "Échec de l\u2019envoi"
      );
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const totalCount = allRequests.length;
  const incompletCount = allRequests.filter((r) => r.status === "incomplet").length;
  const urgentCount = allRequests.filter((r) => r.urgency === "urgent").length;

  const handleStatusFilter = (value: string) => {
    setFilterStatus(value === filterStatus ? "" : value);
  };

  const handleModalityFilter = (value: string) => {
    setFilterModality(value === filterModality ? "" : value);
  };

  const formatDate = (dateStr: string) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString("fr-FR", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  };

  return (
    <div>
      {/* Stats bar */}
      <div className="flex items-center gap-6 mb-6">
        <div className="flex items-center gap-2">
          <span className="text-3xl font-bold text-gray-900">{totalCount}</span>
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
            Demandes
          </span>
        </div>
        <div className="w-px h-10 bg-gray-300" />
        <div className="flex items-center gap-2">
          <span className="text-3xl font-bold text-orange-500">{incompletCount}</span>
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
            Incomplètes
          </span>
        </div>
        <div className="w-px h-10 bg-gray-300" />
        <div className="flex items-center gap-2">
          <span className="text-3xl font-bold text-red-500">{urgentCount}</span>
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
            Urgentes
          </span>
        </div>
        <div className="flex-1" />
        <label
          className={`cursor-pointer inline-flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-semibold text-white ${
            uploading
              ? "bg-gray-400 cursor-not-allowed"
              : "bg-emerald-600 hover:bg-emerald-700"
          }`}
        >
          + Nouvelle demande
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            accept=".txt,.eml,.pdf,.png,.jpg,.jpeg,.tiff,.tif"
            onChange={handleUpload}
            disabled={uploading}
          />
        </label>
      </div>

      {/* Filter pills */}
      <div className="flex items-center gap-2 mb-6 flex-wrap">
        {STATUS_FILTERS.map((f) => (
          <button
            key={f.value}
            onClick={() => handleStatusFilter(f.value)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
              filterStatus === f.value || (f.value === "" && filterStatus === "")
                ? "bg-blue-600 text-white"
                : "bg-white text-gray-700 border border-gray-300 hover:bg-gray-100"
            }`}
          >
            {f.label}
          </button>
        ))}
        <div className="w-px h-6 bg-gray-300 mx-1" />
        {MODALITY_FILTERS.map((f) => (
          <button
            key={f.value}
            onClick={() => handleModalityFilter(f.value)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
              filterModality === f.value
                ? "bg-blue-600 text-white"
                : "bg-white text-gray-700 border border-gray-300 hover:bg-gray-100"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {uploadError && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md text-red-700 text-sm">
          {uploadError}
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-16">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
          <span className="ml-3 text-gray-500">Chargement...</span>
        </div>
      ) : requests.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-xl shadow-sm">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="mx-auto h-12 w-12 text-gray-300"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
            />
          </svg>
          <p className="mt-4 text-gray-500">Aucune demande.</p>
          <p className="text-sm text-gray-400 mt-1">
            Utilisez{" "}
            <code className="bg-gray-100 px-1.5 py-0.5 rounded text-gray-600">
              make demo
            </code>{" "}
            pour ingérer les échantillons, ou importez un fichier ci-dessus.
          </p>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {requests.map((req) => {
            const statusInfo = STATUS_LABELS[req.status] || {
              label: req.status,
              color: "bg-gray-100 text-gray-800 border-gray-300",
            };
            return (
              <Link
                key={req.id}
                href={`/requests/${req.id}`}
                className="block bg-white rounded-xl border border-gray-200 px-6 py-5 hover:shadow-md hover:border-gray-300 transition-all"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <div className="mt-1.5 w-3 h-3 rounded-full bg-gray-300 shrink-0" />
                    <div>
                      <div className="font-semibold text-gray-900 text-base">
                        {req.patient_name || "(Inconnu)"}
                      </div>
                      <div className="text-sm text-gray-500 mt-0.5">
                        {req.modality
                          ? MODALITY_LABELS[req.modality] || req.modality
                          : "—"}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span
                      className={`inline-flex px-3 py-1 rounded-full text-xs font-semibold border ${statusInfo.color}`}
                    >
                      {statusInfo.label}
                    </span>
                    {req.missing_count > 0 && (
                      <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-orange-100 text-orange-700 text-xs font-bold border border-orange-300">
                        {req.missing_count}
                      </span>
                    )}
                  </div>
                </div>
                <div className="text-right mt-1">
                  <span className="text-xs text-gray-400">
                    {formatDate(req.created_at)}
                  </span>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
