import { useEffect, useState } from 'react'

import './App.css'
import Sidebar from './components/Sidebar'
import {
  fetchHealth,
  fetchMetricsSummary,
  planTrip,
  recommendPois,
  runEvaluation,
  runPipeline,
} from './lib/api'
import MetricsSection from './sections/MetricsSection'
import OverviewSection from './sections/OverviewSection'
import PipelineSection from './sections/PipelineSection'
import RecommendationSection from './sections/RecommendationSection'
import SystemStatusSection from './sections/SystemStatusSection'
import TripPlanningSection from './sections/TripPlanningSection'

const sections = [
  { id: 'overview', label: 'Overview' },
  { id: 'poi', label: 'POI Recommendation' },
  { id: 'trip', label: 'Trip Planning' },
  { id: 'pipeline', label: 'Full Pipeline' },
  { id: 'status', label: 'System Status' },
  { id: 'metrics', label: 'Metrics' },
]

const recommendationDefaults = {
  weather_label: 'Clear',
  travel_mode_label: 'car',
  census_division: 'Pacific',
  region_tier: 'Metropolis',
  hour: 14,
  day_of_week: 4,
  top_k: 5,
}

const tripDefaults = {
  org: 'New York, NY',
  dest: 'Los Angeles, CA',
  days: 3,
  budget: 1500,
  people_number: 1,
  constraint_text: '',
  query: 'I want to explore cultural sites, local food, and iconic attractions.',
  poi_ids: [],
}

const pipelineDefaults = {
  recommendation: recommendationDefaults,
  trip: {
    org: 'San Francisco, CA',
    dest: 'Seattle, WA',
    days: 3,
    budget: 1800,
    people_number: 1,
    constraint_text: '',
    query: 'Plan a food-friendly city break with good viewpoints and cultural stops.',
  },
}

export default function App() {
  const [activeSection, setActiveSection] = useState('overview')
  const [health, setHealth] = useState(null)
  const [metrics, setMetrics] = useState(null)
  const [statusLoading, setStatusLoading] = useState(false)

  const [recommendationForm, setRecommendationForm] = useState(recommendationDefaults)
  const [recommendationState, setRecommendationState] = useState({
    loading: false,
    error: '',
    result: null,
  })

  const [tripForm, setTripForm] = useState(tripDefaults)
  const [tripState, setTripState] = useState({
    loading: false,
    error: '',
    result: null,
  })

  const [pipelineForm, setPipelineForm] = useState(pipelineDefaults)
  const [pipelineState, setPipelineState] = useState({
    loading: false,
    error: '',
    result: null,
  })

  const [evaluationState, setEvaluationState] = useState({
    loading: false,
    error: '',
    result: null,
  })

  useEffect(() => {
    refreshStatus()
  }, [])

  async function refreshStatus() {
    setStatusLoading(true)
    try {
      const [healthData, metricsData] = await Promise.all([
        fetchHealth(),
        fetchMetricsSummary(),
      ])
      setHealth(healthData)
      setMetrics(metricsData)
    } catch {
      setHealth({
        status: 'offline',
        db_connected: false,
        model_ready: false,
        llm_configured: false,
        mlflow_enabled: false,
        mlflow_connected: false,
        mlflow_tracking_uri: null,
        mlflow_ui_url: null,
        mlflow_experiment_name: null,
        mlflow_registered_model_name: null,
        mlflow_register_model: false,
        mlflow_latest_alias: null,
        mlflow_champion_alias: null,
        provider: 'groq',
        model: 'unknown',
      })
    } finally {
      setStatusLoading(false)
    }
  }

  async function handleRecommend() {
    setRecommendationState({ loading: true, error: '', result: null })
    try {
      const result = await recommendPois(recommendationForm)
      setRecommendationState({ loading: false, error: '', result })
    } catch (error) {
      setRecommendationState({
        loading: false,
        error: error.message,
        result: null,
      })
    }
  }

  async function handleTripPlan() {
    setTripState({ loading: true, error: '', result: null })
    try {
      const result = await planTrip(tripForm)
      setTripState({ loading: false, error: '', result })
      refreshStatus()
    } catch (error) {
      setTripState({
        loading: false,
        error: error.message,
        result: null,
      })
    }
  }

  async function handlePipelineRun() {
    setPipelineState({ loading: true, error: '', result: null })
    try {
      const result = await runPipeline(pipelineForm)
      setPipelineState({ loading: false, error: '', result })
      refreshStatus()
    } catch (error) {
      setPipelineState({
        loading: false,
        error: error.message,
        result: null,
      })
    }
  }

  async function handleEvaluationRun() {
    setEvaluationState({ loading: true, error: '', result: null })
    try {
      const result = await runEvaluation({ sample_size: 5 })
      setEvaluationState({ loading: false, error: '', result })
      refreshStatus()
    } catch (error) {
      setEvaluationState({
        loading: false,
        error: error.message,
        result: null,
      })
    }
  }

  function importPoiIntoTrip() {
    const poiIds =
      recommendationState.result?.items?.map((item) => item.poi_id) ?? []
    setTripForm((current) => ({ ...current, poi_ids: poiIds }))
  }

  function renderActiveSection() {
    switch (activeSection) {
      case 'overview':
        return (
          <OverviewSection
            health={health}
            metrics={metrics}
            lastRecommendations={recommendationState.result?.items ?? []}
          />
        )
      case 'poi':
        return (
          <RecommendationSection
            form={recommendationForm}
            onChange={(field, value) =>
              setRecommendationForm((current) => ({ ...current, [field]: value }))
            }
            onSubmit={handleRecommend}
            loading={recommendationState.loading}
            error={recommendationState.error}
            result={recommendationState.result}
          />
        )
      case 'trip':
        return (
          <TripPlanningSection
            form={tripForm}
            onChange={(field, value) =>
              setTripForm((current) => ({ ...current, [field]: value }))
            }
            onSubmit={handleTripPlan}
            onImportPoi={importPoiIntoTrip}
            recommendedItems={recommendationState.result?.items ?? []}
            loading={tripState.loading}
            error={tripState.error}
            result={tripState.result}
          />
        )
      case 'pipeline':
        return (
          <PipelineSection
            form={pipelineForm}
            onChange={(group, field, value) =>
              setPipelineForm((current) => ({
                ...current,
                [group]: { ...current[group], [field]: value },
              }))
            }
            onSubmit={handlePipelineRun}
            loading={pipelineState.loading}
            error={pipelineState.error}
            result={pipelineState.result}
          />
        )
      case 'status':
        return (
          <SystemStatusSection
            health={health}
            metrics={metrics}
            onRefresh={refreshStatus}
            loading={statusLoading}
          />
        )
      case 'metrics':
        return (
          <MetricsSection
            metrics={metrics}
            evaluationResult={evaluationState.result}
            onRunEvaluation={handleEvaluationRun}
            loading={evaluationState.loading}
            error={evaluationState.error}
          />
        )
      default:
        return null
    }
  }

  return (
    <div className="shell">
      <Sidebar
        sections={sections}
        activeSection={activeSection}
        onSelect={setActiveSection}
        health={health}
      />
      <main className="main">{renderActiveSection()}</main>
    </div>
  )
}
