"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

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
  a_valider: { label: "A valider", color: "bg-blue-100 text-blue-800" },
  route: { label: "Route", color: "bg-purple-100 text-purple-800" },
};

const MODALITY_LABELS: Record<string, string> = {
  scanner: "Scanner",
  IRM: "IRM",
  doppler: "Doppler",
  echo: "Echo",
  radio: "Radio",
  autre: "Autre",
};

export default function InboxPage() {
  const [requests, setRequests] = useState<RequestSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState<string>("");
  const [filterModality, setFilterModality] = useState<string>("");

  useEffect(() => {
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
  }, [filterStatus, filterModality]);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">
          Boite de reception
        </h2>
        <div className="flex gap-3">
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-1.5 text-sm"
          >
            <option value="">Tous les statuts</option>
            <option value="complet">Complet</option>
            <option value="incomplet">Incomplet</option>
            <option value="a_valider">A valider</option>
            <option value="route">Route</option>
          </select>
          <select
            value={filterModality}
            onChange={(e) => setFilterModality(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-1.5 text-sm"
          >
            <option value="">Toutes les modalites</option>
            <option value="scanner">Scanner</option>
            <option value="IRM">IRM</option>
            <option value="doppler">Doppler</option>
            <option value="echo">Echo</option>
            <option value="radio">Radio</option>
            <option value="autre">Autre</option>
          </select>
        </div>
      </div>

      {loading ? (
        <p className="text-gray-500">Chargement...</p>
      ) : requests.length === 0 ? (
        <p className="text-gray-500">
          Aucune demande. Utilisez{" "}
          <code className="bg-gray-100 px-1 rounded">make demo</code> pour
          ingerer les echantillons.
        </p>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Patient
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Modalite
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
                      {req.urgency || "routine"}
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
                        <span className="text-red-600 font-medium">
                          {req.missing_count}
                        </span>
                      ) : (
                        <span className="text-green-600">0</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {req.source_filename || "—"}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(req.created_at).toLocaleDateString("fr-FR")}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
