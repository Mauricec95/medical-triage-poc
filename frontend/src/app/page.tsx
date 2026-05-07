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
  complet: { label: "Complet", color: "bg-green-100 text-green-800" },
  incomplet: { label: "Incomplet", color: "bg-yellow-100 text-yellow-800" },
  a_valider: { label: "À valider", color: "bg-blue-100 text-blue-800" },
  route: { label: "Routé", color: "bg-purple-100 text-purple-800" },
};

const MODALITY_LABELS: Record<string, string> = {
  scanner: "Scanner",
  IRM: "IRM",
  doppler: "Doppler",
  echo: "Écho",
  radio: "Radio",
  autre: "Autre",
};

const URGENCY_STYLES: Record<string, string> = {
  urgent: "text-red-700 font-semibold",
  prioritaire: "text-orange-600 font-medium",
  routine: "text-gray-600",
};

export default function InboxPage() {
  const [requests, setRequests] = useState<RequestSummary[]>([]);
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

  useEffect(() => {
    fetchRequests();
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
    } catch (err) {
      setUploadError(
        err instanceof Error ? err.message : "Échec de l\u2019envoi"
      );
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  return (
    <div>
      {/* Header bar */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">Boîte de réception</h2>
        <div className="flex items-center gap-3">
          {/* Upload button */}
          <label
            className={`cursor-pointer inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium text-white ${
              uploading
                ? "bg-gray-400 cursor-not-allowed"
                : "bg-blue-600 hover:bg-blue-700"
            }`}
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
                d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5-5m0 0l5 5m-5-5v12"
              />
            </svg>
            {uploading ? "Envoi en cours\u2026" : "Importer un fichier"}
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              accept=".txt,.eml,.pdf,.png,.jpg,.jpeg,.tiff,.tif"
              onChange={handleUpload}
              disabled={uploading}
            />
          </label>

          {/* Filters */}
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm bg-white"
          >
            <option value="">Tous les statuts</option>
            <option value="complet">Complet</option>
            <option value="incomplet">Incomplet</option>
            <option value="a_valider">À valider</option>
            <option value="route">Routé</option>
          </select>
          <select
            value={filterModality}
            onChange={(e) => setFilterModality(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm bg-white"
          >
            <option value="">Toutes les modalités</option>
            <option value="scanner">Scanner</option>
            <option value="IRM">IRM</option>
            <option value="doppler">Doppler</option>
            <option value="echo">Écho</option>
            <option value="radio">Radio</option>
            <option value="autre">Autre</option>
          </select>
        </div>
      </div>

      {uploadError && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md text-red-700 text-sm">
          {uploadError}
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-16">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
          <span className="ml-3 text-gray-500">Chargement…</span>
        </div>
      ) : requests.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-lg shadow">
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
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Patient
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Modalité
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Urgence
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Statut
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Manquants
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Source
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {requests.map((req) => {
                const statusInfo = STATUS_LABELS[req.status] || {
                  label: req.status,
                  color: "bg-gray-100 text-gray-800",
                };
                const urgencyClass =
                  URGENCY_STYLES[req.urgency || "routine"] ||
                  URGENCY_STYLES.routine;
                return (
                  <tr key={req.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Link
                        href={`/requests/${req.id}`}
                        className="text-blue-600 hover:text-blue-800 font-medium"
                      >
                        {req.patient_name || "(Inconnu)"}
                      </Link>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {req.modality
                        ? MODALITY_LABELS[req.modality] || req.modality
                        : "—"}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={urgencyClass}>
                        {req.urgency === "urgent"
                          ? "URGENT"
                          : req.urgency === "prioritaire"
                            ? "Prioritaire"
                            : "Routine"}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${statusInfo.color}`}
                      >
                        {statusInfo.label}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-center">
                      {req.missing_count > 0 ? (
                        <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-red-100 text-red-700 text-xs font-bold">
                          {req.missing_count}
                        </span>
                      ) : (
                        <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-green-100 text-green-700 text-xs font-bold">
                          0
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 max-w-[160px] truncate">
                      {req.source_filename || "—"}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(req.created_at).toLocaleDateString("fr-FR", {
                        day: "2-digit",
                        month: "2-digit",
                        year: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>

          {/* Summary bar */}
          <div className="bg-gray-50 px-6 py-3 border-t border-gray-200 text-sm text-gray-500">
            {requests.length} demande{requests.length > 1 ? "s" : ""}
            {filterStatus || filterModality ? " (filtrées)" : ""}
          </div>
        </div>
      )}
    </div>
  );
}
