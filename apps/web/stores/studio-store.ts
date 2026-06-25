import { create } from 'zustand'
import type { GarmentCategory, JobStatus } from '@vfs/shared-types'

interface BatchGarment {
  id: string
  name: string
  image_url: string
  category: GarmentCategory
}

interface BatchJob {
  garmentId: string
  garmentName: string
  jobId: string | null
  status: JobStatus | null
  resultUrl: string | null
  errorMessage: string | null
}

interface StudioState {
  activePhoto: { url: string; r2_key: string } | null
  selectedGarment: {
    id?: string
    image_url: string
    name?: string
    category: GarmentCategory
  } | null
  selectedCategory: GarmentCategory | null
  currentJobId: string | null
  jobStatus: JobStatus | null
  resultUrl: string | null
  resultMetadata: Record<string, unknown> | null
  errorMessage: string | null
  isGenerating: boolean

  // Batch mode
  batchMode: boolean
  batchGarments: BatchGarment[]
  batchJobs: BatchJob[]
  isBatchGenerating: boolean

  setActivePhoto: (photo: { url: string; r2_key: string } | null) => void
  setSelectedGarment: (garment: StudioState['selectedGarment']) => void
  setCategory: (category: GarmentCategory) => void
  setJobId: (jobId: string) => void
  setJobStatus: (status: JobStatus) => void
  setResult: (url: string, metadata?: Record<string, unknown>) => void
  setError: (message: string) => void
  reset: () => void

  // Batch actions
  toggleBatchMode: () => void
  addBatchGarment: (garment: BatchGarment) => void
  removeBatchGarment: (garmentId: string) => void
  clearBatchGarments: () => void
  setBatchJobs: (jobs: BatchJob[]) => void
  updateBatchJob: (garmentId: string, update: Partial<BatchJob>) => void
  resetBatch: () => void
}

const initialState = {
  activePhoto: null,
  selectedGarment: null,
  selectedCategory: null,
  currentJobId: null,
  jobStatus: null,
  resultUrl: null,
  resultMetadata: null,
  errorMessage: null,
  isGenerating: false,
  batchMode: false,
  batchGarments: [] as BatchGarment[],
  batchJobs: [] as BatchJob[],
  isBatchGenerating: false,
}

export const useStudioStore = create<StudioState>((set) => ({
  ...initialState,

  setActivePhoto: (photo) => set({ activePhoto: photo }),
  setSelectedGarment: (garment) => set({ selectedGarment: garment }),
  setCategory: (category) => set({ selectedCategory: category }),
  setJobId: (jobId) =>
    set({ currentJobId: jobId, isGenerating: true, errorMessage: null }),
  setJobStatus: (status) => set({ jobStatus: status }),
  setResult: (url, metadata) =>
    set({
      resultUrl: url,
      resultMetadata: metadata || null,
      jobStatus: 'done',
      isGenerating: false,
    }),
  setError: (message) =>
    set({
      errorMessage: message,
      jobStatus: 'error',
      isGenerating: false,
    }),
  reset: () => set(initialState),

  // Batch actions
  toggleBatchMode: () =>
    set((state) => ({ batchMode: !state.batchMode, selectedGarment: null, batchGarments: [] })),
  addBatchGarment: (garment) =>
    set((state) => ({
      batchGarments: state.batchGarments.some((g) => g.id === garment.id)
        ? state.batchGarments
        : [...state.batchGarments, garment],
    })),
  removeBatchGarment: (garmentId) =>
    set((state) => ({
      batchGarments: state.batchGarments.filter((g) => g.id !== garmentId),
    })),
  clearBatchGarments: () => set({ batchGarments: [] }),
  setBatchJobs: (jobs) => set({ batchJobs: jobs, isBatchGenerating: true }),
  updateBatchJob: (garmentId, update) =>
    set((state) => ({
      batchJobs: state.batchJobs.map((j) =>
        j.garmentId === garmentId ? { ...j, ...update } : j,
      ),
    })),
  resetBatch: () =>
    set({ batchGarments: [], batchJobs: [], isBatchGenerating: false }),
}))
